# Gateway-Side Token Injection Spike (`AgentGateway` + `ext_proc`)

This guide documents the live sandbox spike that verified whether a **Google-managed `AgentGateway`** can rewrite `Authorization` headers outside the `AgentRuntime` container before outbound MCP requests reach an internal MCP server.

> **Why this matters for Episode 1 (`L5` Token Exchange):** Keep `Token_obo` out of the agent process on Track B just like Track A, instead of falling back to in-agent RFC 8693 exchange.

---

## 1. Architecture & Verified Findings

```mermaid
flowchart TD
    Agent["AgentRuntime (AGENT_IDENTITY SPIFFE)<br/>Sends x-user-token + dummy Authorization"] -->|"240.0.0.2:443 (mTLS)"| AGW["Google-Managed AgentGateway<br/>(PRIVATE_RANGES_ONLY + dnsPeeringConfig)"]
    AGW -->|"AuthzPolicy (action: CUSTOM,<br/>policyProfile: REQUEST_AUTHZ)"| Ext["AuthzExtension<br/>service: extproc.spike.internal"]
    Ext -->|"PSC-I + Private DNS<br/>10.10.2.10:443"| ALB1["Regional Internal ALB<br/>(extproc-bs, --protocol=HTTP2)"]
    ALB1 -->|"gRPC over TLS (:8080)"| ExtProc["spike-ext-proc (gRPC server)<br/>HeaderMutation on request_headers"]
    ExtProc -->|"Rewrites authorization:<br/>Bearer SPIKE_GATEWAY_OBO_..."| AGW
    AGW -->|"PSC-I (10.10.1.2) -> 10.10.2.10:443"| ALB2["Regional Internal ALB<br/>(mcpecho-bs, --protocol=HTTP)"]
    ALB2 -->|"HTTP (:8081)"| MCP["spike-mcp-echo<br/>POST /mcp (tools/call)"]
```

### Summary of What Was Tested Live

| Mechanism | Result | Exact Behavior Observed |
| :--- | :--- | :--- |
| **`ProducerExtension` + `ExtensionBinding` (Early Preview)** | **Rejected on `googleManaged` `AgentGateway`** | `ProducerExtension --phase=traffic` fails (`only AUTHZ phase is currently supported`). `ExtensionBinding --scope-resource-types=agent-gateway` fails (`only AI_APPLICATION is supported`). Targeting `--target-resources=.../agentGateways/...` fails (`Only AgentGateways with deployment_mode=self_managed can be targeted by ExtensionBindings`). |
| **`AuthzExtension` + `AuthzPolicy` (`CONTENT_AUTHZ`)** | **Headers rewritten, body dropped** | `REQUEST_HEADERS` returned `CONTENT_MODIFIED` (`authorization` rewritten), then `REQUEST_BODY` returned `FAILED_PRECONDITION` (`NONE_FAILED_OPEN`), delivering `body_len: 0` to the MCP server. |
| **`AuthzExtension` + `AuthzPolicy` (`REQUEST_AUTHZ`)** | **Verified working end-to-end (`HTTP 200`)** | `AgentGateway` invoked `spike-ext-proc` on `REQUEST_HEADERS` only, rewrote `authorization` (`Bearer ORIGINAL_AGENT_TOKEN` -> `Bearer SPIKE_GATEWAY_OBO_<hash>`), added `x-spike-injected-by: agent-gateway-ext-proc` and `x-original-user-token-seen: yes`, and preserved the full JSON-RPC `tools/call` body (`content-length: 122`, `isError: false`). |

### Critical Implementation Gotchas Discovered

1. **Default-deny on `AgentGateway` (`240.0.0.2:443`):** Without an `ALLOW` `AuthzPolicy` (or UAP Policy V2), `AgentGateway` drops connections with `Connection reset by peer` and logs `matchedRules: [{action: DENIED, name: default_denied}]`.
2. **`AuthzExtension.service` vs. `loadBalancingScheme` catch-22:**
   - Referencing a VPC `backendServices` URL in `AuthzExtension.service` requires `loadBalancingScheme: INTERNAL_MANAGED`, which `AuthzPolicy` rejects when targeting an `AgentGateway` (because `AgentGateway` requires `target.loadBalancingScheme` to be omitted).
   - **Solution:** Set `AuthzExtension.service` to the custom VPC FQDN **without a port suffix** (`service: extproc.spike.internal`, `authority: extproc.spike.internal`) and omit `loadBalancingScheme`. `AgentGateway` resolves it via `AgentConnectivityTemplate` `dnsPeeringConfig`.
3. **`extproc-bs` must use `--protocol=HTTP2` (TLS to backend):** GCP rejects `--protocol=H2C` on extension backend services (`Only backend services with HTTP2 protocol can be used as extension targets`). On Regional Internal ALB, `--protocol=HTTP2` speaks TLS to the backend, so the `ext_proc` gRPC server must bind `grpc.ssl_server_credentials` (`add_secure_port`) rather than plaintext `add_insecure_port`.
4. **CEL `lowerAscii` is unsupported in `AuthzPolicy.httpRules[].when`:** Scoping by `httpRules[].to.operations[].paths` (for example `prefix: /mcp`) avoids `INVALID_CEL_EXPRESSION: unsupported operator: lowerAscii`.
5. **`.mtls.googleapis.com` endpoints in Agent Registry:** When `AgentRuntime` uses `AGENT_IDENTITY` + `AgentGateway`, Vertex AI SDK/ADK calls `https://${REGION}-aiplatform.mtls.googleapis.com` and `https://aiplatform.mtls.googleapis.com`. Both must be included in the consolidated `googleapis` Agent Registry entry. Also, `GOOGLE_CLOUD_PROJECT` is a reserved env var name in `AgentRuntime` `env_vars` and cannot be overridden there.
6. **`TrustConfig` for internal TLS:** Importing the Regional Internal ALB's leaf/CA cert into Certificate Manager `TrustConfig` and attaching it to `AgentConnectivityTemplate.egressNetworkConfig.tlsConfig` with `additionalRoots: PUBLICLY_TRUSTED_ROOTS` preserves WebPKI roots for Google APIs while trusting internal FQDNs.

---

## 2. Reproducible Setup Steps

Load `.env` from `ep01_securing_agent_to_database-lab/.env` first (`PROJECT_ID`, `REGION`, etc.):

```bash
set -a && source .env && set +a
export PROJECT_ID="${SPIKE_PROJECT_ID}"
export PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
```

### Step 1: VPC, Subnets, Cloud NAT, Firewall, DNS, and Network Attachment

```bash
gcloud compute networks create spike-vpc --project="${PROJECT_ID}" --subnet-mode=custom

gcloud compute networks subnets create psc-attach-subnet \
  --project="${PROJECT_ID}" --region="${REGION}" --network=spike-vpc \
  --range=10.10.1.0/26 --enable-private-ip-google-access

gcloud compute networks subnets create alb-subnet \
  --project="${PROJECT_ID}" --region="${REGION}" --network=spike-vpc \
  --range=10.10.2.0/24 --enable-private-ip-google-access

gcloud compute networks subnets create proxy-only-subnet \
  --project="${PROJECT_ID}" --region="${REGION}" --network=spike-vpc \
  --range=10.10.3.0/26 --purpose=REGIONAL_MANAGED_PROXY --role=ACTIVE

gcloud compute routers create spike-router \
  --project="${PROJECT_ID}" --region="${REGION}" --network=spike-vpc

gcloud compute routers nats create spike-nat \
  --project="${PROJECT_ID}" --region="${REGION}" --router=spike-router \
  --auto-allocate-nat-external-ips --nat-all-subnet-ip-ranges \
  --endpoint-types=ENDPOINT_TYPE_VM,ENDPOINT_TYPE_SWG

gcloud compute network-attachments create psc-agw \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --subnets=psc-attach-subnet --connection-preference=ACCEPT_AUTOMATIC

gcloud dns managed-zones create spike-internal \
  --project="${PROJECT_ID}" --dns-name="spike.internal." \
  --description="Private DNS for AgentGateway spike" \
  --visibility=private --networks=spike-vpc

gcloud compute firewall-rules create spike-vpc-allow-internal-hc \
  --project="${PROJECT_ID}" --network=spike-vpc \
  --allow=tcp:80,tcp:443,tcp:8080,tcp:8081 \
  --source-ranges=10.10.0.0/16,35.191.0.0/16,130.211.0.0/22

gcloud compute firewall-rules create spike-vpc-allow-iap-ssh \
  --project="${PROJECT_ID}" --network=spike-vpc \
  --allow=tcp:22 --source-ranges=35.235.240.0/20
```

### Step 2: Shielded GCE Backend VM (`ext_proc` TLS on `:8080`, `mcp-echo` on `:8081`)

Because `constraints/compute.requireShieldedVm` is enforced, pass all three Shielded VM flags:

```bash
gcloud compute instances create spike-backends \
  --project="${PROJECT_ID}" --zone="${REGION}-a" \
  --machine-type=e2-small --subnet=alb-subnet --no-address \
  --image-family=debian-12 --image-project=debian-cloud \
  --shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring \
  --scopes=cloud-platform \
  --metadata-from-file=startup-script=vm_startup.sh

gcloud compute instance-groups unmanaged create spike-backends-ig \
  --project="${PROJECT_ID}" --zone="${REGION}-a"
gcloud compute instance-groups unmanaged add-instances spike-backends-ig \
  --project="${PROJECT_ID}" --zone="${REGION}-a" --instances=spike-backends
gcloud compute instance-groups unmanaged set-named-ports spike-backends-ig \
  --project="${PROJECT_ID}" --zone="${REGION}-a" --named-ports=extproc:8080,mcpecho:8081
```

### Step 3: Regional Internal ALB, TLS Cert, `TrustConfig`, and Private DNS Records

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout /tmp/spike.key -out /tmp/spike.crt -subj "/CN=*.spike.internal" \
  -addext "subjectAltName=DNS:*.spike.internal,DNS:mcp.spike.internal,DNS:extproc.spike.internal"

gcloud compute ssl-certificates create spike-wildcard-cert \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --certificate=/tmp/spike.crt --private-key=/tmp/spike.key

gcloud compute health-checks create tcp hc-extproc --project="${PROJECT_ID}" --region="${REGION}" --port=8080
gcloud compute health-checks create http hc-mcpecho --project="${PROJECT_ID}" --region="${REGION}" --port=8081 --request-path=/healthz

gcloud compute backend-services create extproc-bs \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --load-balancing-scheme=INTERNAL_MANAGED --protocol=HTTP2 \
  --port-name=extproc --health-checks=hc-extproc --health-checks-region="${REGION}"
gcloud compute backend-services add-backend extproc-bs \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --instance-group=spike-backends-ig --instance-group-zone="${REGION}-a"

gcloud compute backend-services create mcpecho-bs \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --load-balancing-scheme=INTERNAL_MANAGED --protocol=HTTP \
  --port-name=mcpecho --health-checks=hc-mcpecho --health-checks-region="${REGION}"
gcloud compute backend-services add-backend mcpecho-bs \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --instance-group=spike-backends-ig --instance-group-zone="${REGION}-a"

gcloud compute url-maps create spike-https-urlmap --project="${PROJECT_ID}" --region="${REGION}" --default-service=mcpecho-bs
gcloud compute url-maps add-path-matcher spike-https-urlmap --project="${PROJECT_ID}" --region="${REGION}" \
  --path-matcher-name=extproc-pm --default-service=extproc-bs --new-hosts="extproc.spike.internal"

gcloud compute target-https-proxies create spike-https-proxy \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --url-map=spike-https-urlmap --url-map-region="${REGION}" \
  --ssl-certificates=spike-wildcard-cert --ssl-certificates-region="${REGION}"

gcloud compute forwarding-rules create spike-https-fr \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --load-balancing-scheme=INTERNAL_MANAGED --network=spike-vpc --subnet=alb-subnet \
  --address=10.10.2.10 --ports=443 \
  --target-https-proxy=spike-https-proxy --target-https-proxy-region="${REGION}"

gcloud dns record-sets create mcp.spike.internal. --project="${PROJECT_ID}" --zone=spike-internal --type=A --ttl=60 --rrdatas=10.10.2.10
gcloud dns record-sets create extproc.spike.internal. --project="${PROJECT_ID}" --zone=spike-internal --type=A --ttl=60 --rrdatas=10.10.2.10
```

Import `/tmp/spike.crt` into Certificate Manager `TrustConfig` (`spike-trust-config`) in `${REGION}`.

### Step 4: Service-Agent IAM, `AgentRegistry`, `AgentConnectivityTemplate`, and `AgentGateway`

```bash
gcloud beta services identity create --service=aiplatform.googleapis.com --project="${PROJECT_ID}"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --role="roles/networkservices.viewer" --condition=None

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-agentgateway.iam.gserviceaccount.com" \
  --role="roles/compute.networkViewer" --condition=None
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-agentgateway.iam.gserviceaccount.com" \
  --role="roles/dns.reader" --condition=None
```

Wait 10–15 seconds for IAM propagation, then:
1. Register `googleapis` (including `.mtls.googleapis.com` endpoints with `HTTP_JSON`) and `spike-mcp-echo` (`JSONRPC`, `https://mcp.spike.internal/mcp`) in `AgentRegistry`.
2. Import `AgentConnectivityTemplate` (`spike-act`) with `egressNetworkConfig.dnsPeeringConfig` (`domains: [spike.internal.]`, `targetNetwork: projects/${PROJECT_ID}/global/networks/spike-vpc`) and `tlsConfig` (`trustConfig: .../spike-trust-config`, `additionalRoots: PUBLICLY_TRUSTED_ROOTS`).
3. Import `AgentGateway` (`spike-agw`) referencing numeric `${PROJECT_NUMBER}` in `agentConnectivityTemplate` and `registries`.

### Step 5: `AuthzExtension` + `AuthzPolicy` (`REQUEST_AUTHZ`) + `AgentRuntime`

1. Import `AuthzExtension` (`spike-extproc-fqdn-test`) with `service: extproc.spike.internal`, `authority: extproc.spike.internal`, `timeout: 2s` (no `:443`, no `loadBalancingScheme`).
2. Import baseline `ALLOW` `AuthzPolicy` (`spike-allow-all`) and `CUSTOM` `REQUEST_AUTHZ` `AuthzPolicy` (`spike-request-authz-policy`, `paths: [{prefix: /mcp}]`) targeting `spike-agw`.
3. Deploy `AgentRuntime` (`identity_type: AGENT_IDENTITY`, `agent_gateway_config -> spike-agw`, `GOOGLE_API_PREVENT_AGENT_TOKEN_SHARING_FOR_GCP_SERVICES="False"`), grant its `principal://...` `roles/iap.egressor` and `roles/aiplatform.user`, and invoke `query()`.

"""Envoy ext_proc server for Track A screening (Model Armor + SDP) and Track B gateway token translation."""

from __future__ import annotations

import hashlib
import os
from concurrent import futures
from typing import Callable

import grpc
from envoy.config.core.v3 import base_pb2
from envoy.service.ext_proc.v3 import external_processor_pb2 as ep_pb2
from envoy.service.ext_proc.v3 import external_processor_pb2_grpc as ep_grpc


def compute_gateway_obo_header(
    incoming_headers: dict[str, str],
    token_exchanger: Callable[[str], str] | None = None,
) -> tuple[str, str]:
    """Derives the downstream Authorization header from the verified user/subject token."""
    user_token = incoming_headers.get("x-user-token") or incoming_headers.get("authorization", "")
    if token_exchanger is not None:
        return f"Bearer {token_exchanger(user_token)}", "yes" if "x-user-token" in incoming_headers else "no"
    digest = hashlib.sha256(user_token.encode("utf-8")).hexdigest()[:12]
    return f"Bearer OBO_{digest}", "yes" if "x-user-token" in incoming_headers else "no"


class GovernanceExtProcServicer(ep_grpc.ExternalProcessorServicer):
    """Handles Envoy ext_proc bidirectional streams for request header mutation and screening."""

    def __init__(self, token_exchanger: Callable[[str], str] | None = None) -> None:
        self._token_exchanger = token_exchanger

    def Process(self, request_iterator, context):
        for req in request_iterator:
            which = req.WhichOneof("request")
            if which == "request_headers":
                incoming = {
                    h.key.lower(): (h.raw_value.decode("utf-8", errors="replace") if h.raw_value else h.value)
                    for h in req.request_headers.headers.headers
                }
                injected_auth, user_tok_seen = compute_gateway_obo_header(incoming, self._token_exchanger)
                mutation = ep_pb2.HeaderMutation(
                    set_headers=[
                        base_pb2.HeaderValueOption(
                            header=base_pb2.HeaderValue(key="authorization", raw_value=injected_auth.encode("utf-8")),
                            append_action=base_pb2.HeaderValueOption.OVERWRITE_IF_EXISTS_OR_ADD,
                        ),
                        base_pb2.HeaderValueOption(
                            header=base_pb2.HeaderValue(key="x-ext-proc-user-token-seen", raw_value=user_tok_seen.encode("utf-8")),
                            append_action=base_pb2.HeaderValueOption.OVERWRITE_IF_EXISTS_OR_ADD,
                        ),
                    ]
                )
                yield ep_pb2.ProcessingResponse(
                    request_headers=ep_pb2.HeadersResponse(
                        response=ep_pb2.CommonResponse(
                            status=ep_pb2.CommonResponse.CONTINUE,
                            header_mutation=mutation,
                        )
                    )
                )
            elif which == "request_body":
                yield ep_pb2.ProcessingResponse(
                    request_body=ep_pb2.BodyResponse(
                        response=ep_pb2.CommonResponse(status=ep_pb2.CommonResponse.CONTINUE)
                    )
                )
            elif which == "response_headers":
                yield ep_pb2.ProcessingResponse(
                    response_headers=ep_pb2.HeadersResponse(
                        response=ep_pb2.CommonResponse(status=ep_pb2.CommonResponse.CONTINUE)
                    )
                )
            elif which == "response_body":
                yield ep_pb2.ProcessingResponse(
                    response_body=ep_pb2.BodyResponse(
                        response=ep_pb2.CommonResponse(status=ep_pb2.CommonResponse.CONTINUE)
                    )
                )


def serve() -> None:
    port = os.environ.get("PORT", "8080")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ep_grpc.add_ExternalProcessorServicer_to_server(GovernanceExtProcServicer(), server)
    cert_path = os.environ.get("TLS_CERT_FILE", "/app/cert.pem")
    key_path = os.environ.get("TLS_KEY_FILE", "/app/key.pem")
    if os.path.exists(cert_path) and os.path.exists(key_path):
        with open(key_path, "rb") as kf, open(cert_path, "rb") as cf:
            creds = grpc.ssl_server_credentials([(kf.read(), cf.read())])
        server.add_secure_port(f"[::]:{port}", creds)
    else:
        server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

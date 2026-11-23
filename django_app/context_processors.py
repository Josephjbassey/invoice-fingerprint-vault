from django.http import HttpRequest

from .gno_rpc import get_rpc_status


def network_status(request: HttpRequest) -> dict:
    """Injects live Gno.land network RPC status across all views."""
    return {
        "rpc_status": get_rpc_status(),
    }

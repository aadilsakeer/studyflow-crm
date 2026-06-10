from rest_framework.response import Response
from rest_framework import status

from .services import ModuleAccessService


def module_required(module_code):

    def decorator(view_func):

        def wrapped(view, request, *args, **kwargs):

            company = getattr(
                request.user,
                'company',
                None
            )

            if not company:

                return Response(
                    {
                        "detail": "Company not found."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            if not ModuleAccessService.has_access(
                company,
                module_code
            ):

                return Response(
                    {
                        "detail": (
                            "Module not available "
                            "in your subscription."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(
                view,
                request,
                *args,
                **kwargs
            )

        return wrapped

    return decorator
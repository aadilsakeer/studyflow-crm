from rest_framework import generics

from licensing.decorators import module_required

from .models import (
    Agent,
    AgentCommission
)

from .serializers import (
    AgentSerializer,
    AgentCommissionSerializer
)


class AgentListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    @module_required('agents')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('agents')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AgentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    @module_required('agents')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('agents')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('agents')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('agents')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AgentCommissionListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = AgentCommission.objects.all()
    serializer_class = AgentCommissionSerializer

    @module_required('agents')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('agents')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AgentCommissionDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = AgentCommission.objects.all()
    serializer_class = AgentCommissionSerializer

    @module_required('agents')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('agents')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('agents')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('agents')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
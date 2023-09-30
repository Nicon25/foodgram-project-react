import csv
from io import StringIO

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (ChangePasswordSerializer, CustomUserCreateSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action in ["list", "create", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action in ["set_password", "me"]:
            return [IsAuthorOrReadOnly()]
        return [permissions.IsAuthenticated()]

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        target_user = self.get_object()
        user = request.user

        if request.method == "POST":
            if target_user == user:
                return Response(
                    {"detail": "Вы не можете подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if Follow.objects.filter(user=user, author=target_user).exists():
                return Response(
                    {"detail": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Follow.objects.create(user=user, author=target_user)

            target_user.is_subscribed = True
            target_user.save()

            return Response(
                {"detail": "Вы подписались на пользователя."},
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            if not Follow.objects.filter(
                user=user, author=target_user
            ).exists():
                return Response(
                    {"detail": "Вы не подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Follow.objects.filter(user=user, author=target_user).delete()

            if not Follow.objects.filter(user=user).exists():
                target_user.is_subscribed = False
                target_user.save()

            return Response(
                {"detail": "Вы отписались от пользователя."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return {}

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        paginator = LimitPagination()
        result_page = paginator.paginate_queryset(follows, request)
        serializer = SubscriptionSerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action == "set_password":
            return ChangePasswordSerializer
        if self.action == "create":
            return CustomUserCreateSerializer
        return UserSerializer

    @action(methods=["post"], detail=False)
    def set_password(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user = request.user
        current_password = request.data.get("current_password", None)
        new_password = request.data.get("new_password", None)
        if not user.check_password(current_password):
            return Response(
                {"error": "Неверный пароль."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Пароль успешно изменен."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=["post"])
    def logout(self, request):
        if IsAuthorOrReadOnly().has_object_permission(
            request, self, request.auth
        ):
            request.auth.delete()
            return Response(status=204)
        return Response({"error": "Доступ запрещен."}, status=401)

    @action(detail=False, methods=["get"])
    def me(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = UserSerializer(user)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [
        permissions.AllowAny,
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action in ["partial_update", "destroy"]:
            return [IsAuthorOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "destroy"]:
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"detail": "Рецепт уже добавлен в список покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ShoppingCart.objects.create(user=user, recipe=recipe)

            return Response(
                {"detail": "Рецепт добавлен в список покупок."},
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            try:
                shopping_cart_item = ShoppingCart.objects.get(
                    user=user, recipe=recipe
                )
            except ShoppingCart.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден в списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            shopping_cart_item.delete()

            return Response(
                {"detail": "Рецепт удален из списка покупок."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return {}

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        ingredient_counts = {}

        for item in shopping_cart_items:
            recipe = item.recipe
            ingredients_in_recipe = IngredientInRecipe.objects.filter(
                recipe=recipe
            )

            for ingredient_in_recipe in ingredients_in_recipe:
                ingredient = ingredient_in_recipe.ingredient
                amount = ingredient_in_recipe.amount

                if ingredient in ingredient_counts:
                    ingredient_counts[ingredient] += amount
                else:
                    ingredient_counts[ingredient] = amount

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["Название ингредиента", "Количество", "Единицы измерения"]
        )

        for ingredient, amount in ingredient_counts.items():
            writer.writerow(
                [ingredient.name, amount, ingredient.measurement_unit]
            )

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.csv"'
        )

        return response

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite, created = Favorites.objects.get_or_create(
            user=user, recipe=recipe
        )

        if request.method == "POST":
            if created:
                return Response(
                    {"detail": "Рецепт добавлен в избранное."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"detail": "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if request.method == "DELETE":
            if not created:
                favorite.delete()
                return Response(
                    {"detail": "Рецепт удален из избранного."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"detail": "Рецепт не найден в избранном."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if request.method == "GET":
            is_favorited = not created
            return Response({"is_favorited": is_favorited})


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [
        permissions.AllowAny,
    ]
    filter_backends = [IngredientFilter, ]
    search_fields = ['^name', ]

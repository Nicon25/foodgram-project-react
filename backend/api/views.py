import csv
from io import StringIO

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow, User

from .filters import RecipeFilter
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
        # Доступ для всех на просмотр юзеров и регистрации
        if self.action in ["list", "create", "retrieve"]:
            return [permissions.AllowAny()]
        # Только владелец аккаунта может смены пароли и
        # просматривать свой профиль
        if self.action in ["set_password", "me"]:
            return [IsAuthorOrReadOnly()]
        # По умолчанию, требуется авторизация
        return [permissions.IsAuthenticated()]

    # Добавляем/удаляем подписки
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

    # Выводим список подписок текущего пользователя
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
        # Сериализатор для смены пароля
        if self.action == "set_password":
            return ChangePasswordSerializer
        # Сериализатор на создание пользователя
        if self.action == "create":
            return CustomUserCreateSerializer
        # Сериализатор для работы с Users
        return UserSerializer

    @action(methods=["post"], detail=False)
    def set_password(self, request):
        # Проверяем, что пользователь авторизован
        if not request.user.is_authenticated:
            return Response(
                {"error": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Получаем текущего пользователя
        user = request.user
        # Получаем старый и новый пароль из данных запроса
        current_password = request.data.get("current_password", None)
        new_password = request.data.get("new_password", None)
        # Проверяем, что старый пароль соответствует текущему
        # паролю пользователя
        if not user.check_password(current_password):
            return Response(
                {"error": "Неверный пароль."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Пароль успешно изменен."},
            status=status.HTTP_204_NO_CONTENT
        )

    # Удаление токена
    @action(detail=False, methods=["post"])
    def logout(self, request):
        if IsAuthorOrReadOnly().has_object_permission(
            request, self, request.auth
        ):
            request.auth.delete()
            return Response(status=204)
        return Response({"error": "Доступ запрещен."}, status=401)

    # Возвращает текущего пользователя
    @action(detail=False, methods=["get"])
    def me(self, request):
        # Получаем текущего залогиненного пользователя
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Сериализуем профиль пользователя и возвращаем его
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
        # Доступ для всех на просмотр списка рецептов
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Только авторизованные могут создавать рецепты
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        # Только автор может изменять и удалять рецепт
        if self.action in ["partial_update", "destroy"]:
            return [IsAuthorOrReadOnly()]
        # По умолчанию, требуется авторизация
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Текущий юзер будет автоматически назначен автором
        # при создании рецепта
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        # Для операции создания используем RecipeCreateSerializer
        if self.action in ["create", "partial_update", "destroy"]:
            return RecipeCreateSerializer
        # Для остальных операций используем RecipeSerializer
        return RecipeSerializer

    # Добавляем, удаляем рецепты в список покупок
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        # Добавляем рецепт в список покупок
        if request.method == "POST":
            # Проверяем, что рецепт еще не добавлен в список
            # текущего пользователя
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"detail": "Рецепт уже добавлен в список покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Добавляем рецепт в список покупок
            ShoppingCart.objects.create(user=user, recipe=recipe)

            return Response(
                {"detail": "Рецепт добавлен в список покупок."},
                status=status.HTTP_201_CREATED,
            )

        # Удаляем рецепт из списка покупок
        if request.method == "DELETE":
            # Проверяем, что рецепт добавлен в список покупок
            # текущего пользователя
            try:
                shopping_cart_item = ShoppingCart.objects.get(
                    user=user, recipe=recipe
                )
            except ShoppingCart.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден в списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Удаляем рецепт из списка покупок
            shopping_cart_item.delete()

            return Response(
                {"detail": "Рецепт удален из списка покупок."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return {}  # пока заглушка

    # Скачиваем список покупок
    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user

        # Получаем список покупок текущего пользователя
        shopping_cart_items = ShoppingCart.objects.filter(user=user)

        # Создаем структуру данных для хранения информации
        # об ингредиентах и их суммарном количестве
        ingredient_counts = {}

        # Проходим по всем элементам списка покупок и обновляем
        # информацию в ingredient_counts
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

        # Создаем объект CSV и записываем данные в него
        output = StringIO()
        writer = csv.writer(output)

        # Заголовок CSV файла
        writer.writerow(
            ["Название ингредиента", "Количество", "Единицы измерения"]
        )

        # Записываем данные ингредиентов в CSV
        for ingredient, amount in ingredient_counts.items():
            writer.writerow(
                [ingredient.name, amount, ingredient.measurement_unit]
            )

        # Создаем HTTPResponse с данными CSV и возвращаем его
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.csv"'
        )

        return response

    # Добавляем, удаляем рецепты в избранное
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
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)

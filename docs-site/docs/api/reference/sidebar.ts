import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "api/reference/be-cooking-api",
    },
    {
      type: "category",
      label: "Recipes",
      items: [
        {
          type: "doc",
          id: "api/reference/get-recipes",
          label: "Получить список рецептов",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/reference/create-recipe",
          label: "Создать новый рецепт",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/reference/get-recipe-by-id",
          label: "Получить рецепт по id",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/reference/update-recipe",
          label: "Обновить рецепт",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "api/reference/delete-recipe",
          label: "Удалить рецепт",
          className: "api-method delete",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;

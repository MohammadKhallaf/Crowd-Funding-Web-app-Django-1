from django.urls import path
from . import views

# app_name = "projects"

urlpatterns = [
    path("viewproject/<int:id>", views.viewdataofproject, name="detail"),
    path("addproject", views.addproject, name="addproject"),
    path(
        "deleteproject/<int:id>",
        views.delete,
        name="delete",
    ),
    path("", views.index),
    path("report/<int:id>", views.report, name="report"),
    path("rate/<int:id>", views.rate, name="rate"),
    path("donate/<int:id>", views.donate, name="donate"),
    path("comment/<int:id>", views.comment, name="comment"),
    path(
        "reportComment/<int:id>/<int:project_id>",
        views.reportComment,
        name="reportComment",
    ),
    path(
        "deleteComment/<int:id>/<int:project_id>",
        views.deleteComment,
        name="deleteComment",
    ),
    path("category/<int:id>", views.category_projects, name="category_projects"),
    path("search", views.search, name="search"),
]

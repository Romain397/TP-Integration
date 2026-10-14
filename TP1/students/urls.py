"""URL routes for the student directory API."""

from django.urls import path

from . import views

urlpatterns = [
    path("students", views.students_collection),
    path("students/stats", views.student_stats),
    path("students/search", views.search_students),
    path("students/<str:raw_id>", views.student_detail),
]
from django.urls import path

from . import views

urlpatterns = [
    path("register", views.reregisterUser, name="registerUser"),
    path("registerUser/post", views.registerUserPost, name="registerUserPost"),
    path("login", views.loginUserPage, name="loginUserPage"),
    path("login/request", views.loginUser, name="loginUser"),
    path("profile", views.profile, name="profile"),
    path("logoutUser", views.logoutUser, name="logoutUser"),
    path("user_data", views.user_data, name="user_data"),
    path("change_password/request", views.change_password, name="change_password"),
    path("delete_account/request", views.delete_account, name="delete_account"),
    path("doctors/<int:num>", views.doctors, name="doctors"),
    path("search_doctors/<str:search_value>/<int:num>", views.search_doctors, name="search_doctors"),
    path("appointements", views.appointements, name="appointements"),
    path("doctor/<str:id>", views.doctor_page, name="doctor_page"),
    path("all_doctors_number", views.all_doctors_number, name="all_doctors_number"),
    path("doctor_data/<str:id>", views.doctor_data, name="doctor_data"),
    path("doctors_schedule/<str:id>", views.doctors_schedule, name="doctors_schedule"),
    path("my-appointements", views.my_appointements,name="my_appointements"),
    path("my_appointements_data/<int:num>", views.my_appointements_data,name="my_appointements_data"),
    path("all_appointements_count", views.all_appointements_count, name="all_appointements_count"),
    path("add_appointement", views.add_appointement, name="add_appointement"),
    path("manage-appointements", views.manage_appointements, name="manage_appointements"),
    path("my_schedule", views.my_schedule, name="my_schedule"),
    path("update_appointement", views.update_appointement, name="update_appointement"),
    path("add_medical_history", views.add_medical_history, name="add_medical_history"),
    path("add_medical_history_data", views.add_medical_history_data, name="add_medical_history_data"),
    path("get_medical_history_data", views.get_medical_history_data, name="get_medical_history_data"),
    path("my_medical_history", views.my_medical_history,name="my_medical_history"),
    path("get_my_medical_history", views.get_my_medical_history, name="get_my_medical_history"),
    path("save_notification", views.save_notification, name="save_notification"),
    path("refuse_med_history_update/<str:id>",views.refuse_med_history_update, name="refuse_med_history_update"),
    path("my_update_requests", views.my_update_requests, name="my_update_requests"),
    path("get_my_notifications", views.get_my_notifications, name="get_my_notifications"),
    path("notifications", views.notifications, name="notifications"),
    path("get_notification_count", views.get_notification_count, name="get_notification_count"),
    path("update_notification_seen/<str:id>", views.update_notification_seen,name="update_notification_seen"),
    path("notifications/<str:id>", views.get_notification, name="get_notification"),
    path("chart", views.get_chart, name="get_chart"),
    path("get_current_notification/<str:id>", views.get_current_notification, name="get_current_notification"),
    path("update_med_history/<str:patient_email>",views.update_med_history, name="update_med_history"),
    path("char_bar_info", views.char_bar_info, name="char_bar_info")
]

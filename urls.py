from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('StudentLogin.html', views.StudentLogin, name="StudentLogin"), 
	       path('AddUser.html', views.AddUser, name="AddUser"),
	       path('AddUserAction', views.AddUserAction, name="AddUserAction"),	
	       path('AdminLoginAction', views.AdminLoginAction, name="AdminLoginAction"),
	       path('TeacherLogin.html', views.TeacherLogin, name="TeacherLogin"),
	       path('TeacherLoginAction', views.TeacherLoginAction, name="TeacherLoginAction"),
	       path('ViewQuestions', views.ViewQuestions, name="ViewQuestions"),
	       path('ViewMarks', views.ViewMarks, name="ViewMarks"),
	       path('AddQuestion', views.AddQuestion, name="AddQuestion"),
	       path('AddQuestionAction', views.AddQuestionAction, name="AddQuestionAction"),
	       path('ViewTeacherMarks', views.ViewTeacherMarks, name="ViewTeacherMarks"),
	       path('WriteExam', views.WriteExam, name="WriteExam"), 
	       path('WriteExamAction', views.WriteExamAction, name="WriteExamAction"), 	
	       path('ViewStudentMarks', views.ViewStudentMarks, name="ViewStudentMarks"),	
	       path('StudentLoginAction', views.StudentLoginAction, name="StudentLoginAction"),
]

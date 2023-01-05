from django.urls import path
from . import views
from .feeds import LatestPostFeed



app_name = 'blog'

urlpatterns = [
# post views
path('', views.post_list, name='post_list'),

#path('', views.PostListView.as_view(), name='post_list'),
path('<int:year>/<int:month>/<int:day>/<slug:post>/',views.post_detail,name='post_detail'),
path('<int:post_id>', views.Post_share, name='post_share'),
path('feed/', LatestPostFeed(), name = 'post_feed'),
path('search/', views.post_search, name='post_search'), 
]
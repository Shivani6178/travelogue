from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_viwes
urlpatterns = [
    path('', views.register, name = 'register'),
    path('index/<str:user>', views.index, name = 'index'),
    path('home', views.home, name = 'home'),
    path('login/', views.loginUser, name = 'loginUser'),
    path('logout/', views.logoutUser, name = 'logoutUser'),
    path('verify/<email_token>', views.verify, name = 'verify'),
    path('error/', views.error, name ='error'),
    path('hotel', views.hotel, name = 'hotel'),
    path('hotel/hotelinfo/<hotel_id>', views.hotelinfo, name = 'hotelinfo'),
    path(r'^hotel/hotelinfo/bookings/(?P<hotel_name>[\w|\W]+)/$', views.bookings, name = 'bookings'),
    path('aboutus', views.aboutus, name = 'aboutus'),
    path('contactus', views.contactus, name = 'contactus'),
    path('destination', views.destination, name = 'destination'),
    path('destination/destinationinfo/<location_id>', views.destinationinfo, name = 'destinationinfo'),
    path('profile/<str:user>', views.profile, name = 'profile'),
    path('transport', views.transport, name = 'transport'),
    path('checkout/<str:email>/<str:hotel_name>/<int:hotel_price>', views.checkout, name= 'checkout'),
    
    path('payment/success/<str:email>', views.success, name= 'success'),
    path('payment/cancel', views.cancel, name= 'cancel'),
    
    
    
    #-------- Password Reset -------
    path('reset_password/', auth_viwes.PasswordResetView.as_view(template_name= 'accounts/password_reset.html'), name = 'reset_password'),
    path('reset_password_sent/',auth_viwes.PasswordResetDoneView.as_view(template_name= 'accounts/password_reset_sent.html'), name = 'password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_viwes.PasswordResetConfirmView.as_view(template_name= 'accounts/password_reset_form.html'), name = 'password_reset_confirm'),
    path('reset_password_complete/', auth_viwes.PasswordResetCompleteView.as_view(template_name= 'accounts/password_reset_done.html'), name = 'password_reset_complete'),
    
]

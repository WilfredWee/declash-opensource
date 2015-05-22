#!/usr/bin/env python2.7

from django.contrib.auth.models import User
if User.objects.count() == 0:
    admin = User.objects.create_user('admin', 'email_here@email.com', 'admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
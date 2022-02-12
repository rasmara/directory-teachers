from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BulkUploadForm
from django.conf import settings
from django.db.models import Q
from .models import *
import csv
import zipfile
import os

# from django.views.generic.edit import FormView
from django.views.generic import View
# from django.core.urlresolvers import reverse_lazy
from django.urls import reverse_lazy


def upload_teachers_from_csv(profiles_csv_file, images_zip_file):
    try:
        bytes_csv_content = profiles_csv_file.file.read()
        text_csv_content = bytes_csv_content.decode('UTF-8').splitlines()
        reader = csv.DictReader(text_csv_content)
        if images_zip_file is not None and zipfile.is_zipfile(images_zip_file):
            with zipfile.ZipFile(images_zip_file) as zfile:
                for t in reader:
                    if not t['Email Address']:
                        continue
                    lst_subject_obj = []
                    for data in t['Subjects taught'].upper().split(','):
                        if len(lst_subject_obj) >= 5:
                            continue
                        if not Subjects.objects.filter(subject_name=data.upper().strip()):
                            Subjects(subject_name=data.upper().strip()).save()
                            get_subject = Subjects.objects.filter(subject_name=data.upper().strip()).first()
                            lst_subject_obj.append(get_subject)
                        else:
                            get_subject = Subjects.objects.filter(subject_name=data.upper().strip()).first()
                            lst_subject_obj.append(get_subject)
                    new_teacher = Teachers(
                        first_name=t['First Name'],
                        last_name=t['Last Name'],
                        email_address=t['Email Address'],
                        phone_number=t['Phone Number'],
                        room_number=t['Room Number'],
                    )
                    new_teacher.save()
                    for item in lst_subject_obj:
                        new_teacher.subjects_taught.add(item)

                    if t['Profile picture'] not in zfile.namelist():
                        with open(os.path.join(settings.MEDIA_ROOT,
                                               'profilepic',
                                               'default.png'),
                                  'rb') as profile_picture_file:
                            new_teacher.profile_pic.save('default.png',
                                                         profile_picture_file,
                                                         True)
                    else:
                        with zfile.open(
                                t['Profile picture']) as profile_picture_file:
                            new_teacher.profile_pic.save(t['Profile picture'],
                                                         profile_picture_file,
                                                         True)

                return True
    except Exception as e:
        return False


class FileUploadView(View):
    form_class = BulkUploadForm
    success_url = reverse_lazy('viewall')
    template_name = 'createrecord.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            if upload_teachers_from_csv(request.FILES['csv_file'],
                                             request.FILES['images_archive']):
                data = Teachers.objects.all()
                messages.success(request, "Data uploaded successfully")
                return render(request, self.success_url, {'data': data})
            messages.error(request, "Invalid File, Please Upload the required file")
            return redirect(self.template_name)


class UploadBulkForm(FormView):
    form_class = BulkUploadForm
    template_name = 'createrecord.html'
    success_url = 'viewall.html'

    def post(self, request, form_class):

        if form_class.is_valid():
            if upload_teachers_from_csv(request.FILES['csv_file'],
                                        request.FILES['images_archive']):
                data = Teachers.objects.all()
                messages.success(request, "Data uploaded successfully")
                return render(request, 'viewall.html', {'data': data})
            messages.error(request, "Invalid File, Please Upload the required file")
            return redirect('createrecord')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

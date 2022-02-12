from django import forms


class BulkUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload required .csv file ",
                               widget=forms.FileInput(attrs={'accept': '.csv'}))
    images_archive = forms.FileField(label="Upload required .zip file",
                                     widget=forms.FileInput(
                                         attrs={'accept': '.zip'}))


class AddNewProfile(forms.Form):

    first_name = forms.CharField()
    last_name = forms.CharField()
    email_address = forms.EmailField()
    phone_number = forms.CharField()
    room_number = forms.CharField()
    subjects = forms.CharField()
    profile_pic = forms.ImageField(label="Upload profile pic",)
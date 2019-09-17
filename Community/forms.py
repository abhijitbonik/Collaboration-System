
from django import forms
from .models import Community, RequestCommunityCreation
from Categories.models import Category
from mptt.forms import TreeNodeChoiceField
import datetime

class CommunityCreateForm(forms.ModelForm):

	x = forms.FloatField(widget=forms.HiddenInput(), required=False)
	y = forms.FloatField(widget=forms.HiddenInput(), required=False)
	width = forms.FloatField(widget=forms.HiddenInput(), required=False)
	height = forms.FloatField(widget=forms.HiddenInput(), required=False)

	class Meta:
		model = Community
		fields = ['name', 'desc', 'image', 'category', 'tag_line', 'created_by']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control'})
		self.fields['desc'].widget.attrs.update({'class': 'form-control'})
		self.fields['image'].widget.attrs.update({'class': 'file', 'data-allowed-file-extensions':'["jpeg", "jpg","png"]', 'data-show-upload':'false', 'data-show-preview':'false', 'data-msg-placeholder':'Select article image for upload...'})
		self.fields['image'].required = False
		self.fields['category'].widget.attrs.update({'class': 'form-control'})
		self.fields['tag_line'].widget.attrs.update({'class': 'form-control'})
		self.fields['created_by'].widget.attrs.update({'class': 'form-control'})
		self.fields['category'] = TreeNodeChoiceField(queryset=Category.objects.all())
		self.fields['category'].required = False

class RequestCommunityCreateForm(forms.ModelForm):
	class Meta:
		model = RequestCommunityCreation
		fields = ['name', 'desc', 'category', 'tag_line', 'purpose']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control', 'ng-model':'name', 'ng-pattern':'/^[a-z A-Z ()]*$/'})
		self.fields['desc'].widget.attrs.update({'class': 'form-control'})
		self.fields['category'].widget.attrs.update({'class': 'form-control'})
		self.fields['tag_line'].widget.attrs.update({'class': 'form-control', 'ng-model':'tag_line', 'ng-pattern': "/^[a-z A-Z0-9 !&()':-]*$/"})
		self.fields['purpose'].widget.attrs.update({'class': 'form-control', 'ng-model':'purpose', 'ng-pattern': "/^[a-z A-Z0-9 !&()':-]*$/"})

class CommunityUpdateForm(forms.ModelForm):

	x = forms.FloatField(widget=forms.HiddenInput(), required=False)
	y = forms.FloatField(widget=forms.HiddenInput(), required=False)
	width = forms.FloatField(widget=forms.HiddenInput(), required=False)
	height = forms.FloatField(widget=forms.HiddenInput(), required=False)

	class Meta:
		model = Community
		fields = ['name', 'desc', 'image', 'category', 'tag_line']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control'})
		self.fields['name'].widget.attrs['readonly'] = True
		self.fields['desc'].widget.attrs.update({'class': 'form-control'})
		self.fields['image'].widget.attrs.update({'class': 'file', 'data-allowed-file-extensions':'["jpeg", "jpg","png"]', 'data-show-upload':'false', 'data-show-preview':'false', 'data-msg-placeholder':'Select article image for upload...'})
		self.fields['image'].required = False
		self.fields['category'].widget.attrs.update({'class': 'form-control'})
		self.fields['tag_line'].widget.attrs.update({'class': 'form-control'})

		if self.instance.parent:
			self.fields['category'] = TreeNodeChoiceField(self.instance.parent.category.get_descendants(include_self=False))
		else:
			self.fields['category'] = TreeNodeChoiceField(queryset=Category.objects.all())
		self.fields['category'].required = False

class SubCommunityCreateForm(forms.ModelForm):
	x = forms.FloatField(widget=forms.HiddenInput(), required=False)
	y = forms.FloatField(widget=forms.HiddenInput(), required=False)
	width = forms.FloatField(widget=forms.HiddenInput(), required=False)
	height = forms.FloatField(widget=forms.HiddenInput(), required=False)

	class Meta:
		model = Community
		fields = ['name', 'desc', 'image', 'category', 'tag_line', 'parent']

	def __init__(self, *args, **kwargs):
		community = kwargs.pop('community', None)
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control'})
		self.fields['desc'].widget.attrs.update({'class': 'form-control'})
		self.fields['image'].widget.attrs.update({'class': 'file', 'data-allowed-file-extensions':'["jpeg", "jpg","png"]', 'data-show-upload':'false', 'data-show-preview':'false', 'data-msg-placeholder':'Select article image for upload...'})
		self.fields['image'].required = False
		self.fields['category'].widget.attrs.update({'class': 'form-control'})
		self.fields['tag_line'].widget.attrs.update({'class': 'form-control'})
		self.fields['tag_line'].required = False
		self.fields['parent'].widget.attrs.update({'class': 'form-control'})
		self.fields['parent'].empty_label = None
		if community:
			self.fields['parent'].queryset = Community.objects.filter(pk=community.pk)
			root = community.get_root()
			if root.category:
				self.fields['category'] = TreeNodeChoiceField(root.category.get_descendants(include_self=False))
			else:
				self.fields['category'].queryset = Category.objects.none()
		self.fields['category'].required = False




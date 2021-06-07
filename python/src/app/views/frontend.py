import requests
import app.consts
import pprint
import datetime
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.core.mail import send_mail
from app.models import Information, Person, Post
from django.core.paginator import Paginator
from django.views.generic import View, TemplateView, FormView
from app.forms import ContactForm, ProfileForm, PostForm, PostEditForm, InformationForm
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string


def make_post_text(self, data):
    open_at = data['open_at']
    close_at = data['close_at']
    registration_open_at = data['registration_open_at']
    registration_close_at = data['registration_close_at']

    if type(open_at) is str:
        open_at = datetime.datetime.fromisoformat(data['open_at'])
    if type(close_at) is str:
        close_at = datetime.datetime.fromisoformat(data['close_at'])

    if type(registration_open_at) is str:
        registration_open_at = datetime.datetime.fromisoformat(data['registration_open_at'])
    if type(registration_close_at) is str:
        registration_close_at = datetime.datetime.fromisoformat(data['registration_close_at'])

    weeks = ['月', '火', '水', '木', '金', '土', '日']

    period = open_at.strftime('%Y年%m月%d日') + '(' + weeks[open_at.weekday()] + ') ' + \
        open_at.strftime('%H:%M') + ' 〜 ' + close_at.strftime('%H:%M')

    registration_period = registration_open_at.strftime('%Y年%m月%d日') + \
        '(' + weeks[registration_open_at.weekday()] + ') ' + \
        registration_open_at.strftime('%H:%M') + ' 〜 ' + \
        registration_close_at.strftime('%Y年%m月%d日') + \
        '(' + weeks[registration_close_at.weekday()] + ') ' + \
        registration_close_at.strftime('%H:%M')

    context = {
        'period': period,
        'registration_period': registration_period, 
        'venue_name': data['venue_name'],          
        'venue_address': data['venue_address'],          
        'latitude': data['latitude'],          
        'longitude': data['longitude'],
        'limit': data['limit'], 
        'fee': data['fee'],
        'url': data['url'],
        'text': data['text'],
        'google_api_key': settings.GOOGLE_API_KEY,
        'google_map_url': settings.GOOGLE_MAP_URL
    }

    return render_to_string('app/post/template.html', context).strip()

# Create your views here.
class Index(TemplateView):
    template_name = 'app/index.html'

    def get_context_data(self):
        PAGE_SIZE = 10

        page = self.request.GET.get(key='page', default=1)

        all_informations = Information.objects \
            .filter(is_public=True) \
            .order_by('updated_at') \
            .reverse()

        pagenator = Paginator(all_informations, PAGE_SIZE)
        informations = pagenator.get_page(page)

        name = ''
        if self.request.user.is_authenticated:
            person = Person.objects \
                .get(user_id=self.request.user.id)
            name = person.first_name + ' ' + person.last_name

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'informations': informations,
            'name': name,
            'notification': notification
        }
        return context
    
class Speedcubing(TemplateView):
    template_name = 'app/speedcubing.html'

class About(TemplateView):
    template_name = 'app/about.html'

class Organization(TemplateView):
    template_name = 'app/organization.html'

class CommunityPostingRequest(TemplateView):
    template_name = 'app/community/posting_request.html'

class CommunityQuestionAndAnswer(TemplateView):
    template_name = 'app/community/question_and_answer.html'

class CommunityAdvise(TemplateView):
    template_name = 'app/community/advise.html'

class InformationList(TemplateView):
    def get(self, request, **kwargs):        
        PAGE_SIZE = 10

        page = self.request.GET.get(key='page', default=1)

        type = kwargs.get('type')
        if type == "":                
            return redirect('index') 

        if type == 'all':
            all_informations = Information.objects \
                .filter(is_public=True) \
                .order_by('updated_at') \
                .reverse()
        else:
            if not type in dict(app.consts.INFORMATION_TYPE_EN):
                return redirect('index') 
            
            type_id = dict(app.consts.INFORMATION_TYPE_EN)[type] 
            all_informations = Information.objects \
                .filter(type=type_id) \
                .filter(is_public=True) \
                .order_by('updated_at') \
                .reverse()
        
        pagenator = Paginator(all_informations, PAGE_SIZE)
        informations = pagenator.get_page(page)

        context = {
            'informations': informations,
            'type': type
        }

        return render(request, 'app/information_list.html', context)

# InformationにするとModel名とかぶるので回避
class InformationDetail(TemplateView):
    def get(self, request, **kwargs):
        id = kwargs.get('id')
        if 0 < id:
            information = Information.objects.filter(id=id)
            if not information.exists():
                return redirect('index')

            information = information.first()

            is_writer = False
            if request.user.is_authenticated and information.person_id == request.user.person.id:
                is_writer = True

            if not information.is_public and not is_writer:
                return redirect('index')

            context = {
                'information': information,
                'title': information.title,
            }

            return render(request, 'app/information.html', context)

        return redirect('index')

class InformationEdit(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')
        
        id = kwargs.get('id')

        information = Information.objects.filter(id=id)
        if not information.exists():
            return redirect('index')
        information = information.first()
        form = InformationForm(initial = {
            'type': information.type,
            'title': information.title,
            'text': information.text,
            'is_public': information.is_public
        })

        if request.user.is_staff:
            if information.person.user.id is not request.user.id:
                return redirect('index')
            form.fields['is_public'].widget.attrs['disabled'] = 'disabled'

        context = {
            'form': form,
            'information': information,
            'notification': ''
        }

        return render(request, 'app/information_edit.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        information_form = InformationForm(request.POST)
        id = kwargs.get('id')

        if information_form.is_valid():
            information = Information.objects.filter(id=id)
            if not information.exists():
                return redirect('index')

            information = information.first()
            information.type = information_form.cleaned_data['type']
            information.title = information_form.cleaned_data['title']
            information.text = information_form.cleaned_data['text']
            information.is_public = information_form.cleaned_data['is_public']
            if request.user.is_staff:
                information.is_public = False

            information.save(update_fields=[
                    'type',
                    'title',
                    'text',
                    'is_public',
                    'updated_at'
            ])

            form = InformationForm(initial = {
                'type': information.type,
                'title': information.title,
                'text': information.text,
                'is_public': information.is_public
            })

            if request.user.is_staff:
                if information.person.user.id is not request.user.id:
                    return redirect('index')
                form.fields['is_public'].widget.attrs['disabled'] = 'disabled'
            
            context = {
                'form': form,
                'information': information,
                'notification': 'is_just_update'
            }

            return render(request, 'app/information_edit.html', context)

class InformationDelete(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        id = kwargs.get('id')

        information = Information.objects.filter(id=id)
        if not information.exists():
            return redirect('index')
        information = information.first()

        context = {
            'information': information,
        }

        return render(request, 'app/information_delete.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        id = kwargs.get('id')

        information = Information.objects.filter(id=id)
        information = information.first()
        if request.user.is_staff and information.person.user.id is not request.user.id:
            return redirect('index')

        Information.objects.filter(id=id).delete()

        request.session['notification'] = 'is_just_information_delete'

        return redirect('post_list')

class PublicAnnouncement(TemplateView):
    template_name = 'app/public_announcement.html'

class Terms(TemplateView):
    template_name = 'app/terms.html'

class TermsOfSale(TemplateView):
    template_name = 'app/terms_of_sale.html'

class PrivacyPolicy(TemplateView):
    template_name = 'app/privacy_policy.html'

class Contact(FormView):
    template_name = 'app/contact.html'
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super(Contact, self).get_context_data(**kwargs)
        context['recaptcha_public_key'] = settings.RECAPTCHA_PUBLIC_KEY
        return context 

    def form_valid(self, form):
        captcha = self.request.POST.get('g-recaptcha-response')
        if captcha:
            auth_url = 'https://www.google.com/recaptcha/api/siteverify?secret={}&response={}'
            auth_url = auth_url.format(settings.RECAPTCHA_SECRET_KEY, captcha)
            response = requests.get(auth_url)
            if response.json().get('success'):
                form.send_email()
                self.request.session['notification'] = 'is_just_contact'
                return redirect('index')

        form.add_error(None, '私はロボットではありませんにチェックを入れてください。')
        return self.form_invalid(form)

class Profile(LoginRequiredMixin, TemplateView):
    def get(self, request):
        form = ProfileForm(initial={
            'prefecture_id': request.user.person.prefecture_id,
        })

        protocol = 'https' if self.request.is_secure() else 'http'
        current_site = get_current_site(self.request)
        domain = current_site.domain
        redirect_uri = protocol + '://' + domain + '/wca/authorization/?type=profile'

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'form': form,
            'wca_oauth_authorization': settings.WCA_OAUTH_AUTHORIZATION,
            'wca_client_id': settings.WCA_CLIENT_ID,
            'stripe_oauth_authorization': settings.STRIPE_OAUTH_AUTHORIZATION,
            'stripe_client_id': settings.STRIPE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'notification': notification
        }
        return render(request, 'app/profile.html', context)

    def post(self, request):
        profile_form = ProfileForm(request.POST)

        if profile_form.is_valid():
            prefecture_id = profile_form.cleaned_data['prefecture_id']

            person = request.user.person
            person.prefecture_id = prefecture_id
            person.save(update_fields=[
                'prefecture_id',
                'updated_at'
            ])
            request.session['notification'] = 'is_just_profile_change'

            return redirect('profile')
    
class PostInput(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not request.user.person.is_community_posting_offer and not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        format = kwargs.get('format')
        if not format:
            return redirect('index')

        if format == 'event':
            form = PostForm()
        elif format == 'information':
            form = InformationForm()
            if request.user.is_staff:
                form.fields['is_public'].widget.attrs['disabled'] = 'disabled'
        else:
            return redirect('index')

        context = {
            'form': form,
            'format': format
        }
        return render(request, 'app/post/input.html', context)

    def post(self, request, **kwargs):
        format = kwargs.get('format')

        if not format:
            return redirect('index')

        if format == 'event':
            form = PostForm(request.POST)
        elif format == 'information':
            form = InformationForm(request.POST)
        else:
            return redirect('index')
        
        if form.is_valid():
            request.session['post_form_data'] = request.POST
            request.session['post_form_data_format'] = format
            return redirect('post_confirm')
        
        context = {
            'form': form,
        }
        return render(request, 'app/post/input.html', context)

class PostConfirm(View):
    def get(self, request):
        session_form_data = request.session.get('post_form_data')
        session_form_data_format = request.session.get('post_form_data_format')

        if not session_form_data or not session_form_data_format:
            return redirect('index')
        
        format = session_form_data_format

        if format == 'event':
            form = PostForm(session_form_data)
            type = app.consts.INFORMATION_TYPE_EVENT
            text = make_post_text(self, form.data)
        elif format == 'information':
            form = InformationForm(session_form_data)
            type = form.data['type']
            text = form.data['text']

        type_display_name = dict(app.consts.INFORMATION_TYPE)[int(type)]

        context = {
            'form': form,
            'text': text,
            'type_display_name': type_display_name,
            'format': format
        }

        return render(request, 'app/post/confirm.html', context)

class PostComplete(View):
    def post(self, request):
        session_form_data = request.session.get('post_form_data')
        session_form_data_format = request.session.get('post_form_data_format')

        if not session_form_data or not session_form_data_format:
            return redirect('post_input')

        del request.session['post_form_data']
        del request.session['post_form_data_format']

        format = session_form_data_format
        if format == 'event':
            form = PostForm(session_form_data)
        elif format == 'information':
            form = InformationForm(session_form_data)

        if form.is_valid():
            if format == 'event':
                type = app.consts.INFORMATION_TYPE_EVENT
                text = make_post_text(self, form.cleaned_data)
            elif format == 'information':
                type = form.cleaned_data['type']
                text = form.cleaned_data['text']

            if request.user.person.is_community_posting_offer:
                post = Post(
                    type=type,
                    title=form.cleaned_data['title'],
                    text=text,
                    person=request.user.person,
                )
                post.save()

                current_site = get_current_site(self.request)
                domain = current_site.domain
                context = {
                    'protocol': 'https' if self.request.is_secure() else 'http',
                    'domain': domain,
                    'post': post,
                }

                subject = render_to_string('mail/post_confirm_subject.txt', context).strip()
                message = render_to_string('mail/post_confirm_message.txt', context).strip()
                send_mail(subject, message, settings.EMAIL_HOST_USER, ['info@speedcubing.or.jp'])

                request.session['notification'] = 'is_just_post_offer'
            elif request.user.is_superuser:
                information = Information(
                    type=type,
                    title=form.cleaned_data['title'],
                    text=text,
                    person=request.user.person,
                    is_public=form.cleaned_data['is_public']
                )
                information.save()
                request.session['notification'] = 'is_just_post'
            elif request.user.is_staff:
                information = Information(
                    type=type,
                    title=form.cleaned_data['title'],
                    text=text,
                    person=request.user.person,
                    is_public=False
                )
                information.save()
                request.session['notification'] = 'is_just_post'

            return redirect('post_list')
            
        return redirect('post_input')
        
class PostList(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.person.is_community_posting_offer and not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        posts = []
        if request.user.person.is_community_posting_offer:
            posts = Post.objects \
                .filter(person__id=request.user.person.id) \
                .order_by('created_at') \
                .reverse()
            informations = Information.objects \
                .filter(person__id=request.user.person.id) \
                .order_by('created_at') \
                .reverse()
        
        if request.user.is_superuser:
            posts = Post.objects.order_by('updated_at').reverse().all()
            informations = Information.objects.order_by('updated_at').reverse().all()
        
        if request.user.is_staff:
            informations = Information.objects \
                .filter(person__id=request.user.person.id) \
                .order_by('created_at') \
                .reverse()

        close_informations = []
        open_informations = []
        for information in informations:
            if information.is_public:
                open_informations.append(information)
            else:
                close_informations.append(information)
        
        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'posts': posts,
            'close_informations': close_informations,
            'open_informations': open_informations,
            'notification': notification,
        }

        return render(request, 'app/post/list.html', context)

class PostDetail(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not request.user.is_superuser:
            return redirect('index')
        
        id = kwargs.get('id')

        post = Post.objects.filter(id=id)
        if not post.exists():
            return redirect('index')
        if post.first().person.id != request.user.person.id:
            return redirect('index')
        
        context = {
            'post': post.first()
        }

        return render(request, 'app/post/detail.html', context)

class PostEdit(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if request.user.person.is_community_posting_offer or not request.user.is_superuser:
            return redirect('index')
        
        id = kwargs.get('id')

        post = Post.objects.filter(id=id)
        if not post.exists():
            return redirect('index')
        post = post.first()
        form = PostEditForm(initial = {
            'title': post.title,
            'text': post.text
        })

        context = {
            'form': form,
            'post': post,
            'notification': ''
        }

        return render(request, 'app/post/edit.html', context)

    def post(self, request, **kwargs):
        if request.user.person.is_community_posting_offer or not request.user.is_superuser:
            return redirect('index')

        post_form = PostEditForm(request.POST)
        id = kwargs.get('id')

        if post_form.is_valid():
            post = Post.objects.filter(id=id)
            if not post.exists():
                return redirect('index')

            post = post.first()
            post.type = app.consts.INFORMATION_TYPE_EVENT
            post.title = post_form.cleaned_data['title']
            post.text = post_form.cleaned_data['text']
            post.save(update_fields=[
                    'type',
                    'title',
                    'text',
                    'updated_at'
            ])

            form = PostEditForm(initial = {
                'title': post.title,
                'text': post.text
            })
            
            context = {
                'form': form,
                'post': post,
                'notification': 'is_just_update'
            }

            return render(request, 'app/post/edit.html', context)

class PostApprove(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if request.user.person.is_community_posting_offer or not request.user.is_superuser:
            return redirect('index')

        id = kwargs.get('id')

        post = Post.objects.filter(id=id)
        if not post.exists():
            return redirect('index')
        post = post.first()

        information = Information(
            type=post.type,
            title=post.title,
            text=post.text,
            is_public=False
        )
        information.person = request.user.person
        information.save()
        # 削除
        Post.objects.filter(id=id).delete()

        request.session['notification'] = 'is_just_post_approve'

        return redirect('post_list')
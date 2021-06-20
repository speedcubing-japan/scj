from django.urls import path

from .views.scj.index import Index
from .views.scj.speedcubing import Speedcubing
from .views.scj.about import About
from .views.scj.organization import Organization
from .views.scj.public_announcement import PublicAnnouncement
from .views.scj.privacy_policy import PrivacyPolicy
from .views.scj.terms import Terms
from .views.scj.terms_of_sale import TermsOfSale
from .views.scj.contact import Contact
from .views.scj.profile import Profile

from .views.information.list import List as InformationList
from .views.information.detail import Detail as InformationDetail
from .views.information.edit import Edit as InformationEdit
from .views.information.delete import Delete as InformationDelete

from .views.wca.about import About as WcaAbout
from .views.wca.holding_policy import HoldingPolicy as WcaHoldingPolicy
from .views.wca.regulation import Regulation as WcaRegulation
from .views.wca.ranking import Ranking as WcaRanking
from .views.wca.authorization import Authorization as WcaAuthorization

from .views.stripe.authorization import Authorization as StripeAuthorization
from .views.stripe.create import Create as StripeCreate
from .views.stripe.webhook import Webhook as StripeWebhook

from .views.community.posting_request import PostingRequest as CommunityPostingRequest
from .views.community.question_and_answer import QuestionAndAnswer as CommunityQuestionAndAnswer
from .views.community.advise import Advise as CommunityAdvise

from .views.post.input import Input as PostInput
from .views.post.confirm import Confirm as PostConfirm
from .views.post.complete import Complete as PostComplete
from .views.post.list import List as PostList
from .views.post.detail import Detail as PostDetail
from .views.post.edit import Edit as PostEdit
from .views.post.approve import Approve as PostApprove

from .views.registration.input import Input as RegistrationInput
from .views.registration.confirm import Confirm as RegistrationConfirm
from .views.registration.execute import Execute as RegistrationExecute
from .views.registration.complete import Complete as RegistrationComplete

from .views.entrance.login import Login
from .views.entrance.logout import Logout

from .views.password.change import Change as PasswordChange
from .views.password.change_complete import ChangeComplete as PasswordChangeComplete
from .views.password.reset import Reset as PasswordReset
from .views.password.reset_complete import ResetComplete as PasswordResetComplete

from .views.mail.change import Change as MailChange
from .views.mail.change_complete import ChangeComplete as MailChangeComplete

from .views.competition.about import About as CompetitionAbout
from .views.competition.regulation import Regulation as CompetitionRegulation
from .views.competition.index import Index as CompetitionIndex
from .views.competition.detail import Detail as CompetitionDetail
from .views.competition.registration import Registration as CompetitionRegistration
from .views.competition.competitor import Competitor as CompetitionCompetitor
from .views.competition.result import Result as CompetitionResult
from .views.competition.schedule import Schedule as CompetitionSchedule
from .views.competition.fee import Fee as CompetitionFee
from .views.competition.admin.index import Index as CompetitionAdminIndex
from .views.competition.admin.refund import Refund as CompetitionAdminRefund
from .views.competition.admin.edit import Edit as CompetitionAdminEdit
from .views.competition.admin.csv import Csv as CompetitionAdminCsv
from .views.competition.admin.wca_csv import WcaCsv as CompetitionAdminWcaCsv

from .views.ranking.index import Index as RankingIndex


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('speedcubing/', Speedcubing.as_view(), name='speedcubing'),
    path('about/', About.as_view(), name='about'),
    path('organization/', Organization.as_view(), name='organization'),
    path('public_announcement/', PublicAnnouncement.as_view(), name='public_announcement'),
    path('privacy_policy/', PrivacyPolicy.as_view(), name='privacy_policy'),
    path('terms/', Terms.as_view(), name='terms'),
    path('terms_of_sale/', TermsOfSale.as_view(), name='terms_of_sale'),
    path('contact/', Contact.as_view(), name='contact'),
    path('profile/', Profile.as_view(), name='profile'),

    path('information/list/<str:type>/', InformationList.as_view(), name='information_list'),
    path('information/<int:id>/', InformationDetail.as_view(), name='information'),
    path('information/edit/<int:id>/', InformationEdit.as_view(), name='information_edit'),
    path('information/delete/<int:id>/', InformationDelete.as_view(), name='information_delete'),

    path('wca/about/', WcaAbout.as_view(), name='wca_about'),
    path('wca/holding_policy/', WcaHoldingPolicy.as_view(), name='wca_holding_policy'),
    path('wca/regulation/', WcaRegulation.as_view(), name='wca_regulation'),
    path('wca/ranking/', WcaRanking.as_view(), name='wca_ranking'),
    path('wca/authorization/', WcaAuthorization.as_view(), name='wca_authorization'),

    path('stripe/authorization/', StripeAuthorization.as_view(), name='stripe_authorization'),
    path('stripe/create/', StripeCreate.as_view(), name='stripe_create'),
    path('stripe/webhook/', StripeWebhook.as_view(), name='stripe_webhook'),

    path('community/posting_request/', CommunityPostingRequest.as_view(), name='community_posting_request'),
    path('community/question_and_answer/', CommunityQuestionAndAnswer.as_view(), name='community_question_and_answer'),
    path('community/advise/', CommunityAdvise.as_view(), name='community_advise'),
    
    path('post/input/<str:format>/', PostInput.as_view(), name='post_input'),
    path('post/confirm/', PostConfirm.as_view(), name='post_confirm'),
    path('post/complete/', PostComplete.as_view(), name='post_complete'),
    path('post/list/', PostList.as_view(), name='post_list'),
    path('post/detail/<int:id>/', PostDetail.as_view(), name='post_detail'),
    path('post/edit/<int:id>/', PostEdit.as_view(), name='post_edit'),
    path('post/approve/<int:id>/', PostApprove.as_view(), name='post_approve'),

    path('registration/input/', RegistrationInput.as_view(), name='registration_input'),
    path('registration/confirm/', RegistrationConfirm.as_view(), name='registration_confirm'),
    path('registration/execute/', RegistrationExecute.as_view(), name='registration_execute'),
    path('registration/complete/<token>/', RegistrationComplete.as_view(), name='registration_complete'),

    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('password/change/', PasswordChange.as_view(), name='password_change'),
    path('password/change/complete/', PasswordChangeComplete.as_view(), name='password_change_complete'),
    path('password/reset/', PasswordReset.as_view(), name='password_reset'),
    path('password/reset/complete/<uidb64>/<token>/', PasswordResetComplete.as_view(), name='password_reset_complete'),

    path('mail/change/', MailChange.as_view(), name='mail_change'),
    path('mail/change/complete/<str:token>/', MailChangeComplete.as_view(), name='mail_change_complete'),

    path('competition_about/', CompetitionAbout.as_view(), name="competition_about"),
    path('competition_regulation/', CompetitionRegulation.as_view(), name="competition_regulation"),
    path('competition/', CompetitionIndex.as_view(), name="competition_index"),
    path('competition/<str:name_id>/', CompetitionDetail.as_view(), name="competition_detail"),
    path('competition/<str:name_id>/registration/', CompetitionRegistration.as_view(), name="competition_registration"),
    path('competition/<str:name_id>/competitior/<str:event_name>/', CompetitionCompetitor.as_view(), name="competition_competitor"),
    path('competition/<str:name_id>/result/', CompetitionResult.as_view(), name="competition_result"),
    path('competition/<str:name_id>/schedule/', CompetitionSchedule.as_view(), name="competition_schedule"),
    path('competition/<str:name_id>/fee/', CompetitionFee.as_view(), name="competition_fee"),
    path('competition/<str:name_id>/admin/', CompetitionAdminIndex.as_view(), name="competition_admin_index"),
    path('competition/<str:name_id>/admin/refund/', CompetitionAdminRefund.as_view(), name="competition_admin_refund"),
    path('competition/<str:name_id>/admin/edit/<int:competitor_id>/', CompetitionAdminEdit.as_view(), name="competition_admin_edit"),
    path('competition/<str:name_id>/admin/csv/', CompetitionAdminCsv.as_view(), name="competition_admin_csv"),
    path('competition/<str:name_id>/admin/wca_csv/', CompetitionAdminWcaCsv.as_view(), name="competition_admin_wca_csv"),

    path('ranking/', RankingIndex.as_view(), name="ranking_index"),
]

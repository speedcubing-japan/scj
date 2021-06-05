from django.urls import path
from .views import frontend
from .views import auth
from .views import competition
from .views import wca
from .views import ranking
from .views import stripe

urlpatterns = [
    path('', frontend.Index.as_view(), name='index'),
    path('information/list/<str:type>/', frontend.InformationList.as_view(), name='information_list'),
    path('information/<int:id>/', frontend.InformationDetail.as_view(), name='information'),
    path('information/edit/<int:id>/', frontend.InformationEdit.as_view(), name='information_edit'),
    path('information/delete/<int:id>/', frontend.InformationDelete.as_view(), name='information_delete'),
    path('speedcubing/', frontend.Speedcubing.as_view(), name='speedcubing'),

    path('wca/about/', wca.WcaAbout.as_view(), name='wca_about'),
    path('wca/holding_policy/', wca.WcaHoldingPolicy.as_view(), name='wca_holding_policy'),
    path('wca/regulation/', wca.WcaRegulation.as_view(), name='wca_regulation'),
    path('wca/ranking/', wca.WcaRanking.as_view(), name='wca_ranking'),
    path('wca/authorization/', wca.WcaAuthorization.as_view(), name='wca_authorization'),

    path('stripe/authorization/', stripe.StripeAuthorization.as_view(), name='stripe_authorization'),
    path('stripe/create/', stripe.StripeCreate.as_view(), name='stripe_create'),
    path('stripe/webhook/', stripe.StripeWebhook.as_view(), name='stripe_webhook'),

    path('community/posting_request/', frontend.CommunityPostingRequest.as_view(), name='community_posting_request'),
    path('community/question_and_answer/', frontend.CommunityQuestionAndAnswer.as_view(), name='community_question_and_answer'),
    path('community/advise/', frontend.CommunityAdvise.as_view(), name='community_advise'),
    
    path('about/', frontend.About.as_view(), name='about'),
    path('organization/', frontend.Organization.as_view(), name='organization'),
    path('public_announcement/', frontend.PublicAnnouncement.as_view(), name='public_announcement'),
    path('privacy_policy/', frontend.PrivacyPolicy.as_view(), name='privacy_policy'),
    path('terms/', frontend.Terms.as_view(), name='terms'),
    path('terms_of_sale/', frontend.TermsOfSale.as_view(), name='terms_of_sale'),
    path('contact/', frontend.Contact.as_view(), name='contact'),
    path('profile/', frontend.Profile.as_view(), name='profile'),

    path('post/input/<str:format>/', frontend.PostInput.as_view(), name='post_input'),
    path('post/confirm/', frontend.PostConfirm.as_view(), name='post_confirm'),
    path('post/complete/', frontend.PostComplete.as_view(), name='post_complete'),
    path('post/list/', frontend.PostList.as_view(), name='post_list'),
    path('post/detail/<int:id>/', frontend.PostDetail.as_view(), name='post_detail'),
    path('post/edit/<int:id>/', frontend.PostEdit.as_view(), name='post_edit'),
    path('post/approve/<int:id>/', frontend.PostApprove.as_view(), name='post_approve'),

    path('registration/input/', auth.RegistrationInput.as_view(), name='registration_input'),
    path('registration/confirm/', auth.RegistrationConfirm.as_view(), name='registration_confirm'),
    path('registration/', auth.Registration.as_view(), name='registration'),
    path('registration/complete/<token>/', auth.RegistrationComplete.as_view(), name='registration_complete'),
    path('login/', auth.Login.as_view(), name='login'),
    path('logout/', auth.Logout.as_view(), name='logout'),
    path('password/change/', auth.PasswordChange.as_view(), name='password_change'),
    path('password/change/complete/', auth.PasswordChangeComplete.as_view(), name='password_change_complete'),
    path('password/reset/', auth.PasswordReset.as_view(), name='password_reset'),
    path('password/reset/complete/<uidb64>/<token>/', auth.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('mail/change/', auth.MailChange.as_view(), name='mail_change'),
    path('mail/change/complete/<str:token>/', auth.MailChangeComplete.as_view(), name='mail_change_complete'),

    path('competition_about/', competition.CompetitionAbout.as_view(), name="competition_about"),
    path('competition_regulation/', competition.CompetitionRegulation.as_view(), name="competition_regulation"),
    path('competition/', competition.CompetitionIndex.as_view(), name="competition_index"),
    path('competition/<str:name_id>/', competition.CompetitionDetail.as_view(), name="competition_detail"),
    path('competition/<str:name_id>/registration/', competition.CompetitionRegistration.as_view(), name="competition_registration"),
    path('competition/<str:name_id>/competitior/<str:event_name>/', competition.CompetitionCompetitor.as_view(), name="competition_competitor"),
    path('competition/<str:name_id>/result/', competition.CompetitionResult.as_view(), name="competition_result"),
    path('competition/<str:name_id>/schedule/', competition.CompetitionSchedule.as_view(), name="competition_schedule"),
    path('competition/<str:name_id>/fee/', competition.CompetitionFee.as_view(), name="competition_fee"),
    path('competition/<str:name_id>/admin/', competition.CompetitionAdmin.as_view(), name="competition_admin"),
    path('competition/<str:name_id>/admin/refund/', competition.CompetitionAdminRefund.as_view(), name="competition_admin_refund"),
    path('competition/<str:name_id>/admin/competitor/csv/', competition.CompetitionAdminCompetitorCsv.as_view(), name="competition_admin_competitor_csv"),
    path('competition/<str:name_id>/admin/competitor/csv/wca_import/', competition.CompetitionAdminCompetitorCsvWcaImport.as_view(), name="competition_admin_competitor_csv_wca_import"),
    path('competition/<str:name_id>/admin/competitor/edit/<int:competitor_id>/', competition.CompetitionAdminCompetitorEdit.as_view(), name="competition_admin_competitor_edit"),

    path('ranking/', ranking.RankingIndex.as_view(), name="ranking_index"),
]

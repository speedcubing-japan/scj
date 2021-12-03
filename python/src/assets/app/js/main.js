$(function () {
  // TableSorter
  $('#competitor, #pending, #registration, #cancel').tablesorter();

  $('select').addClass('custom-select');

  if ($('.registration_terms').prop('checked') && $('.registration_privacy_policy').prop('checked')) {
    $('.registration_submit').prop('disabled', true);
  }

  // 登録時の確認
  $('.registration_terms').change(function () {
    var isTermsChecked = $('.registration_terms').prop('checked');
    var isPrivacyPolicyChecked = $('.registration_privacy_policy').prop('checked');
    if (isTermsChecked && isPrivacyPolicyChecked) {
      $('.registration_submit').prop('disabled', false);
    } else {
      $('.registration_submit').prop('disabled', true);
    }
  });

  $('.registration_privacy_policy').change(function () {
    var isTermsChecked = $('.registration_terms').prop('checked');
    var isPrivacyPolicyChecked = $('.registration_privacy_policy').prop('checked');
    if (isTermsChecked && isPrivacyPolicyChecked) {
      $('.registration_submit').prop('disabled', false);
    } else {
      $('.registration_submit').prop('disabled', true);
    }
  });

  $('.competition_registration_confirm').change(function () {
    var isCompetitonRegistrationConfirm = $('.competition_registration_confirm').prop('checked');
    if (isCompetitonRegistrationConfirm) {
      $('.competition_registration').prop('disabled', false);
    } else {
      $('.competition_registration').prop('disabled', true);
    }
  });

  // Competition検索
  $('.competition_search').change(function () {
    $('form').submit();
  });

  // 翻訳ボタン
  $('.language').click(function () {
    $('#language_select').submit();
  });

  // Ranking検索
  $('.ranking_search').click(function () {
    var value = $(this).val();
    var input = $('<input>')
      .attr('type', 'hidden')
      .attr('name', 'type').val(value);
    $('form').append(input);
    $('form').submit();
  });

  // Ranking検索
  $('.ranking_search_item').change(function () {
    var value = $('.ranking_search.active').val();
    var input = $('<input>')
      .attr('type', 'hidden')
      .attr('name', 'type').val(value);
    $('form').append(input);
    $('form').submit();
  });

  // Competitor検索
  $('.competition_competitor').change(function () {
    if ($(this).val() != '') {
      window.location.href = $(this).val();
    }
  });

  // 大会管理更新
  $('.competition_admin_submit').click(function () {
    var value = $(this).val();
    var input = $('<input>')
      .attr('type', 'hidden')
      .attr('name', 'type').val(value);
    $('form').append(input);
    $('form').attr('action', '');
    $('form').submit();
  });

  // 大会管理全選択
  $('.competition_admin_all_pending').on('click', function () {
    $('.competition_admin_pending').prop('checked', $(this).prop('checked'));
  });
  $('.competition_admin_all_admit').on('click', function () {
    $('.competition_admin_admit').prop('checked', $(this).prop('checked'));
  });
  $('.competition_admin_all_cancel').on('click', function () {
    $('.competition_admin_cancel').prop('checked', $(this).prop('checked'));
  });

  // 大会関連メールアドレス
  $('.competition_admin_checkbox').change(function () {
    var competition_admin_emails = [];
    $('.competition_admin_checkbox').each(function () {
      if ($(this).prop('checked') && $(this).data('email') != undefined) {
        competition_admin_emails.push($(this).data('email'));
      }
    });
    competition_admin_emails_string = competition_admin_emails.join(',');
    $('.competition_admin_email').attr('href', 'mailto:?bcc=' + competition_admin_emails_string);
  });

  // スケジュールラウンド表示
  $('.competition_schedule_event').on('click', function () {
    var isChecked = $(this).prop('checked');
    var eventId = $(this).val();

    $('[id=' + eventId + '_round]').each(function () {
      roundType = $(this).attr('round_type')
      console.error(roundType);
      var value = ''
      if (roundType == 4 || roundType == 7) {
        value = 'table-danger';
      }
      else if (roundType == 3) {
        value = 'table-warning';
      }
      else if (roundType == 2) {
        value = 'table-success';
      }
      else if (roundType == 1) {
        value = 'table-primary';
      }

      if (isChecked) {
        $(this).addClass(value);
      } else {
        $(this).removeClass(value);
      }
    })

  })

  // ボタン用Submit(action変更)
  $('.submit_change_action').click(function () {
    var value = $(this).val();
    $('form').attr('action', value);
    $('form').submit();
  });

  // ボタン用Submit
  $('.submit').click(function () {
    $('form').submit();
  });

  // set cookie
  $('.agree_cookie').click(function () {
    maxAge = 60 * 60 * 24 * 365;
    document.cookie = `agree_cookie=1;max-age=${maxAge}`;
  });

  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
  $('.form-control').removeClass('is-valid');
  $('.dropify').dropify({ messages: { 'default': '' } });
  $('.dropify').change(function () {
    $('.file').submit();
    $('.dropify').value('')
  });

});

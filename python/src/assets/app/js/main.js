$(function(){
  // TableSorter
  $('#competitor, #pending, #registration, #cancel').tablesorter();

  $("select").addClass("custom-select");

  if ($('.registration_terms').prop('checked') && $('.registration_privacy_policy').prop('checked')) {
    $('.registration_submit').prop('disabled', true);
  }

  // 登録時の確認
  $('.registration_terms').change(function() {
    var isTermsChecked = $('.registration_terms').prop('checked');
    var isPrivacyPolicyChecked = $('.registration_privacy_policy').prop('checked');
    if (isTermsChecked && isPrivacyPolicyChecked) {
      $('.registration_submit').prop('disabled', false);
    } else {
      $('.registration_submit').prop('disabled', true);
    }
  });

  $('.registration_privacy_policy').change(function() {
    var isTermsChecked = $('.registration_terms').prop('checked');
    var isPrivacyPolicyChecked = $('.registration_privacy_policy').prop('checked');
    if (isTermsChecked && isPrivacyPolicyChecked) {
      $('.registration_submit').prop('disabled', false);
    } else {
      $('.registration_submit').prop('disabled', true);
    }
  });

  $('.competition_registration_confirm').change(function() {
    var isCompetitonRegistrationConfirm = $('.competition_registration_confirm').prop('checked');
    if (isCompetitonRegistrationConfirm) {
      $('.competition_registration').prop('disabled', false);
    } else {
      $('.competition_registration').prop('disabled', true);
    }
  });

  // Competition検索
  $('.competition_search').change(function() {
    $('form').submit();
  });

  // Ranking検索
  $('.ranking_search').click(function() {
    var value = $(this).val();
    var input = $("<input>")
      .attr("type", "hidden")
      .attr("name", "type").val(value);
    $('form').append(input);
    $('form').submit();
  });

  // Ranking検索
  $('.ranking_search_item').change(function() {
    var value = $('.ranking_search.active').val();
    var input = $("<input>")
      .attr("type", "hidden")
      .attr("name", "type").val(value);
    $('form').append(input);
    $('form').submit();
  });

  // Competitor検索
  $('.competition_competitor').change(function() {
    if ($(this).val() != '') {
      window.location.href = $(this).val();
    }
  });

  // 大会管理更新
  $('.competition_admin_submit').click(function() {
    var value = $(this).val();
    var input = $("<input>")
      .attr("type", "hidden")
      .attr("name", "type").val(value);
    $('form').append(input);
    $('form').attr('action', '');
    $('form').submit();
  });

  // 大会管理全選択
  $('.competition_admin_all_pending').on("click",function(){
    $('.competition_admin_pending').prop("checked", $(this).prop("checked"));
  });
  $('.competition_admin_all_admit').on("click",function(){
    $('.competition_admin_admit').prop("checked", $(this).prop("checked"));
  });
  $('.competition_admin_all_cancel').on("click",function(){
    $('.competition_admin_cancel').prop("checked", $(this).prop("checked"));
  });

  // ボタン用Submit(action変更)
  $('.submit_change_action').click(function() {
    var value = $(this).val();
    $('form').attr('action', value);
    $('form').submit();
  });

  // ボタン用Submit
  $('.submit').click(function() {
    $('form').submit();
  });

  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
});

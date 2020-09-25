export default class Create {
  constructor(selector, csrfToken) {
    this.selector = selector;
    this.container = $(this.selector);
    this.csrfToken = csrfToken;

    this.isAttached = false;
    this.attach();
  }

  attach() {
    if (this.isAttached) return;
    if (this.container.length === 0) return;

    this.attachUI();
    this.attachEvents();
    this.isAttached = true;
  }

  attachUI() {
    this.title = $('#title');
    this.gender = $('#gender');
    this.category = $('#category');
    this.subcategory = $('#subcategory');
    this.detail1 = $('#detail1');
    this.detail2 = $('#detail2');
    this.detail3 = $('#detail3');
    this.detail4 = $('#detail4');
    this.detail5 = $('#detail5');
    this.userCredits = $('#user_credits');
    this.recentDescriptionsSelector = '#recent_descriptions';
    this.outcome = $('#outcome');
    this.spinner = $('.spinner');
  }

  attachEvents() {
    let _this = this;

    $('body').on('submit', this.selector, function () {
      _this.spinner.show();
      _this.container.find('button').prop('disabled', true);
      _this.create();

      return false;
    });
  }

  create() {
    let _this = this;

    let ajaxParams = {
      type: 'POST',
      url: '/create/',
      data: {title: $(this.title).val(), gender: $(this.gender).val(), category: $(this.category).val(),
        subcategory: $(this.subcategory).val(), detail1: $(this.detail1).val(),
        detail2: $(this.detail2).val(), detail3: $(this.detail3).val(),
        detail4: $(this.detail4).val(), detail5: $(this.detail5).val()},
      dataType: 'json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader('X-CSRFToken', _this.csrfToken);
        return _this.outcomeStatus.text('')
          .removeClass('alert-success alert-warning alert-danger alert-info').hide();
      }
    };

    return $.ajax(ajaxParams).done(function (data, status, xhr) {
      let creditsLeft = parseInt(_this.userCredits.text());
      let parsedData = xhr.responseJSON.data;
      let statusHTML = '';
      let createClass = '';
      let alertClass = '';

      _this.userCredits.text(creditsLeft);

      if (parsedData.description) {
        statusHTML = '<i class="far fa-fw fa-smile"></i> Congrats, a new description!';
        createClass = 'success';
        alertClass = 'success';
      } else {
        statusHTML = '<i class="far fa-fw fa-frown"></i> Uh oh, something went wrong on my end.';
        createClass = 'danger';
        alertClass = 'info';
      }

      $(_this.recentDescriptionsSelector).show();

      let recentDescription = `
        <tr>
          <td class="text-warning">
            <i class="fas fa-fw fa-database"></i> ${parsedData.title}
          </td>
          <td>${parsedData.gender}</td>
          <td>${parsedData.category}</td>
          <td>${parsedData.subcategory}</td>
          <td class="text-${createClass}">
            <i class="fas fa-fw fa-database"></i> ${parsedData.description}
          </td>
        </tr>
      `;
      let recentDescriptionCount = $(`${_this.recentDescriptionsSelector} tr`).length;

      $(`${_this.recentDescriptionsSelector} tbody`).prepend(recentDescription);
      if (recentDescriptionCount > 10) {
        $(`${_this.recentDescriptionsSelector} tr:last`).remove();
      }

      return _this.outcomeStatus.addClass(`small alert alert-${alertClass}`)
        .html(statusHTML);
    }).fail(function (xhr, status, error) {
      let statusClass = 'alert-danger';
      let errorMessage = 'You are out of credits. You should buy more.';

      if (xhr.responseJSON) {
        errorMessage = xhr.responseJSON.error;
      } else if (error == 'TOO MANY REQUESTS') {
        errorMessage = 'You have been temporarily rate limited.';
      }

      return _this.outcomeStatus.addClass(statusClass).text(errorMessage);
    }).always(function (xhr, status, error) {
      _this.spinner.hide();
      _this.container.find('button').prop('disabled', false);
      _this.outcomeStatus.show();

      return xhr;
    });
  }
};

from time import sleep

from flask import url_for, json

from lib.tests import ViewTestMixin, assert_status_with_message


class TestCreate(ViewTestMixin):
    def test_create_page(self):
        """ Create page renders successfully. """
        self.login()
        response = self.client.get(url_for('create.create_description'))
        assert response.status_code == 200

    def test_description_history_details(self):
        """ Description history should render successfully. """
        self.login()
        response = self.client.get(url_for('create.history'))

        assert_status_with_message(200, response,
                                   'Description history')

    def test_create_description(self):
        """ Create description works. """
        self.login()

        title = 'Air Jordans'
        gender = 'mens'
        category = 'shoes'
        subcategory = 'sneakers'
        detail1 = 'vamp straps'
        detail2 = 'open toe'
        detail3 = 'soft footbed'
        detail4 = ''
        deatil5 = ''

        params = {
          'title': title,
          'gender': gender,
          'category': category,
          'subcategory': subcategory,
          'detail1': detail1,
          'detail2': detail2,
          'detail3': detail3
        }

        response = self.client.post(url_for('create.create_description'),
                                    data=params, follow_redirects=True)

        data = json.loads(response.data)['data']

        assert 'title' in data
        assert 'gender' in data
        assert 'category' in data
        assert 'subcategory' in data
        assert 'detail1' in data
        assert 'detail2' in data
        assert 'detail3' in data
        assert 'description' in data

    def test_create_description_fails_due_to_no_credits(self):
        """ Create description fails due to no credits. """
        self.login()
        
        title = 'Air Jordans'
        gender = 'mens'
        category = 'shoes'
        subcategory = 'sneakers'
        detail1 = 'vamp straps'
        detail2 = 'open toe'
        detail3 = 'soft footbed'
        detail4 = ''
        deatil5 = ''

        params = {
          'current_user.credits': 0,
          'title': title,
          'gender': gender,
          'category': category,
          'subcategory': subcategory,
          'detail1': detail1,
          'detail2': detail2,
          'detail3': detail3
        }

        response = self.client.post(url_for('create.create_description'),
                                    data=params, follow_redirects=True)

        data = json.loads(response.data)['data']

        assert 'You need more credits bub.' in data['error']

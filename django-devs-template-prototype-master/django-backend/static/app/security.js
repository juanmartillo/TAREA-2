class User {
  constructor(id = undefined, userName, password, email, firstName, lastName) {
    this.id = id;
    this.userName = userName;
    this.password = password;
    this.email = email;
    this.firstName = firstName;
    this.lastName = lastName;
  }
}

class Security {
  constructor(user) {
    this.user = user
  }

  async userLogin() {

    const formData = new FormData();

    formData.append('username', this.user.userName)
    formData.append('password', this.user.password)

    const options = {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      body: formData
    }

    const response = await fetch('/security/login', options)
    if (!response.ok) {
      throw response
    }
    return await response.json()

  }

}

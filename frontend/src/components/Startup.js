const Startup = () => {
  return (
    <div>
      <head>
        <title>Easy Route</title>
      </head>

      <body>
        <div className="header">
          <div className="title">Easy Route</div>
          <div className="sub-title">Your one-stop-shop for trip planning</div>

          <p>
            Welcome to the Easy Route <br /> The code running this page can be
            found <a href="https://github.com/usef-kh/easyroute">here</a>
          </p>

          <div className="options">
            <form
              //   action="{{url_for('signup')}}"
              className="add-form"
              method="GET"
            >
              <input type="submit" value="Sign Up" className="btn btn-block" />
            </form>

            <form
              // action="{{url_for('login')}}"
              className="add-form"
              method="GET"
            >
              <input type="submit" value="Login" className="btn btn-block" />
            </form>
          </div>
        </div>
      </body>
    </div>
  );
};

export default Startup;

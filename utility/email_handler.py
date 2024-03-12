def OPT_Template(reciever_name, Otp, custom_message= "OTP for the email verification"):
    html_template = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
    
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
            }}
    
            h1 {{
                color: #333;
            }}
            button {{
                  background-color: black;
                  border: none;
                  color: white;
                  padding: 20px;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 16px;
                  margin: 4px 2px;
                  border-radius: 12px;
                }}
            p {{
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{reciever_name}, Welcome to the AR Power</h1>
            <p>{custom_message}</p>
            <center><button>OTP : {Otp}</button></center>
        </div>
    </body>
    </html>
    '''
    return html_template


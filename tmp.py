from apps.emailModule.outlook import OutlookEmail
outlook = OutlookEmail()

def main():
    is_true, token = outlook.get_access_token('M.C522_SN1.0.U.-CvLcu*kGkiCdbwiHOo!8HGHlvQLmfqRaqAeSMQ9Vndi2PDojSYOIp7JdGhw7wjOAdkBngV!NBK!2Y5unWqa88*x*PJ!k9uWJRDPx1c7jAmlGcUe1mHTTST9Di8vef2IXTjP3h0O6!qZ2GTb4nQv86hraoQKyCBujDg5*pTVnFd62oeiWYKPpTvSRH5Gx7XNGbkXZrp7zI09C4dFgYuUgFmGf0MHWkW1UoR5!V3*2KlBOI7r1rxQZH8qfCzTSipQP5RAa07ELj2uvi6VIiGhDZafnv!JlLYFabTXQlN3If5Hy9nVqdG*J*PMpMel2IOD345E0cOtaYaNyvWWLuiWVs3y6Os!0p5n2VHX4TvuPI5vZq15gFcMX*0ikAZkt3uuBbGw!82KWrO0Qf6Qj!Yg7KUXW5eTy7d1iXAPJ!oEg2pVW')
    if is_true:
        print(token)
    else:
        print("wrong token")
if __name__ == "__main__":
    main()
    
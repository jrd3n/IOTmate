import webbrowser

def open_pga(smo):
    
    pgaURL = "https://pga.bsigroup.com/Search/JobSearch.aspx?SMONumberequals={}".format(smo)

    webbrowser.open(pgaURL)

def open_dradis():

    dradisURL = "https://10.81.253.200"

    webbrowser.open(dradisURL)

if __name__ == "__main__":

    # open_pga("3555157")

    oped_dradis()
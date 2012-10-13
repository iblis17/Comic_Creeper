/***************************************************************
 * Name:      creeperMain.h
 * Purpose:   Defines Application Frame
 * Author:     ()
 * Created:   2012-09-23
 * Copyright:  ()
 * License:
 **************************************************************/

#ifndef creeperMAIN_H
#define creeperMAIN_H

#ifndef WX_PRECOMP
    #include <wx/wx.h>
#endif

#include "creeperApp.h"
#include <wx/stattext.h>
#include <wx/gdicmn.h>
#include <wx/sstream.h>
#include <wx/socket.h>
#include <string>
#include <wx/sckstrm.h>

#include <curl/curl.h>


class creeperFrame: public wxFrame
{
    public:
		creeperFrame(wxFrame *frame, const wxString& title);
		~creeperFrame();

    private:
        enum
        {
            idMenuQuit = 1000,
            idMenuAbout,
            idContent,
            idPanel,
            idSearchBtn,
            idSocket,
            idSInput
        };
        void OnClose(wxCloseEvent& event);
        void OnQuit(wxCommandEvent& event);
        void OnAbout(wxCommandEvent& event);
        void SearchBtn(wxCommandEvent& event);
        void SocketEvn(wxSocketEvent& event);
		void GetWebdata(const char *, const char *);

        wxStaticText *creeperContent;
		wxPanel *creeperPanel;
		wxButton *creeperSearchBtn;
		wxString creeperSocketData;
		wxTextCtrl *creeperSInput;	// For Search Input

        DECLARE_EVENT_TABLE()
};

size_t write_data(char *buffer, size_t size, size_t nmemb, void *userp);

#endif // creeperMAIN_H

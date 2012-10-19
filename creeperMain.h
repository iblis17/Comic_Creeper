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

#include	"creeperApp.h"
#include	<wx/stattext.h>
#include	<wx/gdicmn.h>
#include	<wx/sstream.h>
#include	<wx/socket.h>
#include	<wx/sckstrm.h>

#include	<curl/curl.h>

#include	<string>
#include	<fstream>

#include	<iconv.h>

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
            idSInput,
            idClearBtn,
            idFileList
        };
        void OnClose(wxCloseEvent& event);
        void OnQuit(wxCommandEvent& event);
        void OnAbout(wxCommandEvent& event);
        void SearchBtn(wxCommandEvent& event);
        void SocketEvn(wxSocketEvent& event);
		int GetWebdata(const char *, const char *);
		void ClearBtn(wxCommandEvent& event);
		std::string Getcview(const char *file);
		void GetImgCode(const char*);
		void GetComicIndex(const char*);

        wxStaticText *creeperContent;
		wxPanel *creeperPanel;
		wxButton *creeperSearchBtn;
		wxString creeperSocketData;
		wxTextCtrl *creeperSInput;	// For Search Input
		wxButton *creeperClearBtn;
		wxStaticText *creeperFileList;
		wxString TmpDir;

        DECLARE_EVENT_TABLE()
};

size_t write_data(char *buffer, size_t size, size_t nmemb, void *userp);

#endif // creeperMAIN_H

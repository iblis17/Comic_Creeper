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
#include    <wx/protocol/http.h>

#include	<curl/curl.h>

#include	<string>
#include	<fstream>
#include	<sstream>
#include	<vector>

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
            idStatusPanel,
            idSearchBtn,
			idClearBtn,
            idSocket,
            idSInput,
            idFileList,
            idDebugBtn
        };
        void OnClose(wxCloseEvent& event);
        void OnQuit(wxCommandEvent& event);
        void OnAbout(wxCommandEvent& event);
        void SearchBtn(wxCommandEvent& event);
		void ClearBtn(wxCommandEvent& event);
		void GetIndexBtn(std::string);
		void DebugBtn(wxCommandEvent& event);
        void SocketEvn(wxSocketEvent& event);
		int GetWebdata(const char *, const char *);
		int GetWebdata(wxString, wxString, std::string, int);
		std::string Getcview(const char *file);
		void GetImgCode(const char*);
		void GetComicIndex(const char*);
		bool convert(const char*, const char*, char*, size_t, char*, size_t);
		int ConvertFile(const char*);

		wxPanel *creeperPanel;
		wxPanel *creeperStatusPanel;
		wxButton *creeperSearchBtn;
		wxButton *creeperClearBtn;
		wxButton *creeperDebugBtn;
		wxString creeperSocketData;
		wxString TmpDir;
		wxString indexConv;
		wxStaticText *creeperContent;
		wxStaticText *creeperFileList;
		wxTextCtrl *creeperSInput;	// For Search Input
		wxBoxSizer *vStatBox;
		wxStaticBoxSizer *hIndexBox;
		wxGridSizer *hIndexTable;
		std::vector<int> idIndexBtn;	//Starting from 2000
		static const int idIndexBtnBase;
		std::vector<wxButton *> IndexBtn;


        DECLARE_EVENT_TABLE()
};

size_t write_data(char *buffer, size_t size, size_t nmemb, void *userp);

#endif // creeperMAIN_H

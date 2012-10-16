/***************************************************************
 * Name:      creeperMain.cpp
 * Purpose:   Code for Application Frame
 * Author:     ()
 * Created:   2012-09-23
 * Copyright:  ()
 * License:
 **************************************************************/

#ifdef WX_PRECOMP
#include "wx_pch.h"
#endif

#ifdef __BORLANDC__
#pragma hdrstop
#endif //__BORLANDC__

#include "creeperMain.h"

//helper functions
enum wxbuildinfoformat {
    short_f, long_f };

// Fetch Data from Curl
std::string userdata;

wxString wxbuildinfo(wxbuildinfoformat format)/*{{{*/
{
    wxString wxbuild(wxVERSION_STRING);

    if (format == long_f )
    {
#if defined(__WXMSW__)
        wxbuild << _T("-Windows");
#elif defined(__WXMAC__)
        wxbuild << _T("-Mac");
#elif defined(__UNIX__)
        wxbuild << _T("-Linux");
#endif

#if wxUSE_UNICODE
        wxbuild << _T("-Unicode build");
#else
        wxbuild << _T("-ANSI build");
#endif // wxUSE_UNICODE
    }

    return wxbuild;
}/*}}}*/

BEGIN_EVENT_TABLE(creeperFrame, wxFrame)/*{{{*/
    EVT_CLOSE(creeperFrame::OnClose)
    EVT_MENU(idMenuQuit, creeperFrame::OnQuit)
    EVT_MENU(idMenuAbout, creeperFrame::OnAbout)
    EVT_BUTTON(idSearchBtn, creeperFrame::SearchBtn)
    EVT_SOCKET(idSocket, creeperFrame::SocketEvn)
    EVT_TEXT_ENTER(idSInput, creeperFrame::SearchBtn)
    EVT_BUTTON(idClearBtn, creeperFrame::ClearBtn)
END_EVENT_TABLE()/*}}}*/

creeperFrame::creeperFrame(wxFrame *frame, const wxString& title)/*{{{*/
    : wxFrame(frame, -1, title, wxPoint(-1, -1), wxSize(450, 300))
{
#if wxUSE_MENUS
    // create a menu bar
    wxMenuBar* mbar = new wxMenuBar();
    wxMenu* fileMenu = new wxMenu(_T(""));
    fileMenu->Append(idMenuQuit, _("&Quit\tAlt-F4"), _("Quit the application"));
    mbar->Append(fileMenu, _("&File"));

    wxMenu* helpMenu = new wxMenu(_T(""));
    helpMenu->Append(idMenuAbout, _("&About\tF1"), _("Show info about this application"));
    mbar->Append(helpMenu, _("&Help"));

    SetMenuBar(mbar);
#endif // wxUSE_MENUS

#if wxUSE_STATUSBAR
    // create a status bar with some information about the used wxWidgets version
    CreateStatusBar(1);
    SetStatusText(_("Ready"),0);
    //SetStatusText(wxbuildinfo(short_f), 1);
#endif // wxUSE_STATUSBAR

	// create StaticText for showing content

	creeperPanel = new wxPanel(this, idPanel,
							wxDefaultPosition, wxDefaultSize,
							0, _("ContentPanel"));

	creeperContent = new wxStaticText(creeperPanel, idContent, _("Comic ID"));
	//							wxPoint(10, 10), wxSize(100, 100),
	//							wxALIGN_LEFT, _("idContent"));

	creeperSearchBtn = new wxButton(creeperPanel, idSearchBtn, _("Commit"),
								wxDefaultPosition, wxDefaultSize,
								0, wxDefaultValidator, _("SearchBtn"));

	creeperSInput = new wxTextCtrl(creeperPanel, idSInput, _(""),
								wxDefaultPosition, wxSize(100, -1));
	creeperSInput->SetMaxLength(5);

	creeperClearBtn = new wxButton(creeperPanel, idClearBtn, _("Clear"),
								wxDefaultPosition, wxDefaultSize);

	creeperFileList = new wxStaticText(creeperPanel, idFileList, _(""));
	TmpDir = _("./tmp/");

	wxBoxSizer *hbox1 = new wxBoxSizer(wxHORIZONTAL);
	wxBoxSizer *hbox2 = new wxBoxSizer(wxHORIZONTAL);
	wxBoxSizer *vbox = new wxBoxSizer(wxVERTICAL);

	vbox->Add(-1, 10);
	hbox1->Add(creeperContent, 0, wxTOP, 2);
	hbox1->Add(creeperSInput, 0, wxRIGHT | wxLEFT, 10);
	hbox1->Add(creeperSearchBtn, 0, wxRIGHT, 5);
	hbox1->Add(creeperClearBtn, 0);
	vbox->Add(hbox1, 0, wxLEFT | wxRIGHT, 10);
	vbox->Add(-1, 10);
	hbox2->Add(creeperFileList, 1);
	vbox->Add(hbox2, 1, wxEXPAND | wxRIGHT | wxLEFT, 10);
	creeperPanel->SetSizer(vbox);

	Centre();
}/*}}}*/

creeperFrame::~creeperFrame()/*{{{*/
{
}/*}}}*/

void creeperFrame::OnClose(wxCloseEvent &event)/*{{{*/
{
    Destroy();
}/*}}}*/

void creeperFrame::OnQuit(wxCommandEvent &event)/*{{{*/
{
    Destroy();
}/*}}}*/

void creeperFrame::OnAbout(wxCommandEvent &event)/*{{{*/
{
    wxString msg = _("Creeper for 8comic!\nYour sys:\t") + wxGetOsDescription();
    wxMessageBox(msg, _("Welcome to..."));
}/*}}}*/

void creeperFrame::SearchBtn(wxCommandEvent& event)/*{{{*/
{
	if(creeperSInput->IsEmpty())
	{
		SetStatusText(_("Please input ComicID."));
		return;
	}

	wxString Url(_("http://www.8comic.com/html/"));
	wxString DestFile(TmpDir);
	std::string CodeUrl, DestCode;

	Url += creeperSInput->GetValue() + _(".html");
	DestFile += creeperSInput->GetValue() + _(".html");

	wxCharBuffer host = Url.ToUTF8();
	wxCharBuffer dest = DestFile.ToUTF8();

	if ( GetWebdata(host.data(), dest.data()) != 0)
	{
		creeperFileList->SetLabel( creeperFileList->GetLabel() + _("Fail to get:") + Url + _("\n"));
		return;
	}

	creeperFileList->SetLabel( creeperFileList->GetLabel() + DestFile + _("\n"));
	CodeUrl = Getcview(dest.data());

	if(CodeUrl == "Error")
	{
		return;
	}

	CodeUrl += creeperSInput->GetValue().mb_str();
	CodeUrl += ".html";
	DestCode = TmpDir.mb_str();
	DestCode += creeperSInput->GetValue().mb_str();
	DestCode += "-code.html";
	/*wxString ss(CodeUrl.c_str(), wxConvUTF8);
	wxMessageBox(ss);
	*/

	if( GetWebdata(CodeUrl.c_str(), DestCode.c_str()) != 0)
	{
		wxString ts(CodeUrl.c_str(), wxConvUTF8);
		creeperFileList->SetLabel( creeperFileList->GetLabel() + _("Fail to get:") + ts + _("\n"));
		return;
	}

	wxString ts(DestCode.c_str(), wxConvUTF8);
	creeperFileList->SetLabel( creeperFileList->GetLabel() + ts + _("\n"));
	//GetWebdata("http://www.8comic.com", "./tmp/creeperHtml");
	//GetWebdata("http://www.8comic.com/html/7483.html", "./tmp/7483.html");
}/*}}}*/

void creeperFrame::SocketEvn(wxSocketEvent& event)/*{{{*/
{
	wxSocketBase *client = event.GetSocket();
	wxSocketInputStream in(*client);
	wxStringOutputStream out(&creeperSocketData);

	if(in.IsOk())
	{
		in.Read(out);
		wxMessageBox(creeperSocketData);
		client->Close();
		SetStatusText(_("Connect Closed!"));
	}
}/*}}}*/

int creeperFrame::GetWebdata(const char *host, const char *path)/*{{{*/
{
	CURL *creeperHTTP;
	CURLcode req;
	char err[CURL_ERROR_SIZE];
	FILE *userfile;

	userfile = fopen(path, "w+");
	userdata = "";
	creeperHTTP = curl_easy_init();
	curl_easy_setopt(creeperHTTP, CURLOPT_WRITEFUNCTION, NULL);
	curl_easy_setopt(creeperHTTP, CURLOPT_WRITEDATA, userfile);
	curl_easy_setopt(creeperHTTP, CURLOPT_ERRORBUFFER, err);
	curl_easy_setopt(creeperHTTP, CURLOPT_URL, host);
	SetStatusText(_("Curl Loading."));
	req = curl_easy_perform(creeperHTTP);

	if(req != 0)
	{
		wxMessageBox( wxString::FromUTF8(err) );
		SetStatusText(_("Curl Fail!"));
		curl_easy_cleanup(creeperHTTP);
		return 1;
	}
	else
	{
		SetStatusText(_("Curl success!"));
	}

	curl_easy_cleanup(creeperHTTP);
	fclose( userfile );
	return 0;
}/*}}}*/

size_t write_data(char *buffer, size_t size, size_t nmemb, void *userp)/*{{{*/
{
	//userdata += buffer;
	//wxMessageBox( wxString::Format(_("%i"), size));
	return (size*nmemb);
}/*}}}*/

void creeperFrame::ClearBtn(wxCommandEvent& event)/*{{{*/
{
	creeperSInput->Clear();
}/*}}}*/

std::string creeperFrame::Getcview(const char *file)/*{{{*/
{
	std::ifstream cview;
	std::string catid, baseurl;
	cview.open(file);

	if( !cview.is_open() )
	{
		return "Error";
	}
	while(cview >> catid)
	{
		size_t pos = catid.find("cview(");
		if( pos != std::string::npos )
		{
			catid = catid.substr(pos);
			size_t pos1 = catid.find(",");
			size_t pos2 = catid.find(")");
			catid = catid.substr(pos1 + 1 , pos2 - pos1 - 1);
			break;
		}
	}
	if(catid=="4" ||
		catid=="6" ||
		catid=="12" ||
		catid=="22" )
			baseurl="http://www.8comic.com/show/cool-";
	else if(catid=="1" ||
			catid=="17" ||
			catid=="19" ||
			catid=="21" )
			baseurl="http://www.8comic.com/show/cool-";
	else if(catid=="2" ||
			catid=="5" ||
			catid=="7" ||
			catid=="9" )
			baseurl="http://www.8comic.com/show/cool-";
	else if(catid=="10" ||
			catid=="11" ||
			catid=="13" ||
			catid=="14" )
			baseurl="http://www.8comic.com/show/best-manga-";
	else if(catid=="3" ||
			catid=="8" ||
			catid=="15" ||
			catid=="16" ||
			catid=="18" ||
			catid=="20" )
			baseurl="http://www.8comic.com/show/best-manga-";
	else
	{
		SetStatusText(_("Getcview Fail!"));
	}

	cview.close();
	return baseurl;
	
	//const char *host = "http://www.8comic.com/js/comicview.js";
	//const char *dest = "./tmp/comicview.js";
	//std::ifstream cview;
	//std::string tmp;
	//int k = 0;

	//if ( GetWebdata(host, dest) != 0)
	//{
	//	SetStatusText(_("Getcview Fail!"));
	//}

	//cview.open(dest);

	//if( !cview.is_open() )
	//{
	//	return;
	//}

	//while( cview >> tmp)
	//{
	//	if( tmp.substr(0, 4) == "////")
	//	{
	//		k++;
	//		if( k == 2)
	//			break;
	//	}
	//	size_t pos = tmp.find("atid==");
	//	if( pos != std::string::npos)
	//	{
	//		tmp = tmp.substr( pos + 6 );
	//		for(int i=0; i<tmp.size(); i++)
	//		{
	//			if( (tmp[i] < '1') || (tmp[i] > '9') )
	//			{
	//				tmp = tmp.substr(0, i);
	//			}
	//		}
	//	}
	//	wxString ss(tmp.c_str(), wxConvUTF8);
	//	wxMessageBox(ss);
	//}
	//cview.close();
	
}/*}}}*/

	/* Fetch html data using wxURL ==================
	wxURL *creeperURL = new wxURL(_("http://www.8comic.com"));
	if(creeperURL->GetError() == wxURL_NOERR)
	{
		wxString data;
		wxInputStream *in = creeperURL->GetInputStream();

		if(in && in->IsOk())
		{
			SetStatusText(_("URL Ready"));
			wxStringOutputStream outdata(&data);
			in->Read(outdata);
			wxMessageBox(data , _("Search"));
		}
		delete in;
	}
	*//*}}}*/
	/* Fetch html dada using wxHTTP =================
	wxHTTP creeperHTTP;
	creeperHTTP.SetHeader(_("Content-Type"), _("text/html;"));
	//creeperHTTP.SetHeader(_("Referer"), _("http://www.8comic.com/"));
	//creeperHTTP.SetHeader(_("Cookie"), _("origin_num=2"));
	creeperHTTP.SetHeader(_("User-Agent"), _("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4"));

	SetStatusText(_("Conneting..."));
	for(int i=0; i<5; i++)
	{
		if( !creeperHTTP.Connect(_("www.8comic.com")) )
		//if( !creeperHTTP.Connect(_("cnmc24.hs.ntnu.edu.tw")) )
		{
			SetStatusText(_("Connect Fail! Retry..."));
		}
		else
		{
			SetStatusText(_("Connect successfully!"));
			break;
		}

		if(i == 4)
		{
			creeperHTTP.Abort();
			SetStatusText(_("Connect Fail! Abort."));
			return;
		}
	}

	wxInputStream *in = creeperHTTP.GetInputStream(_("/"));
	wxString data;
	wxStringOutputStream outdata(&data);

	//wxSleep(5);
	in->Read(outdata);

	wxMessageBox(data);
	*//*}}}*/

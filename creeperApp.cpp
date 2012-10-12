/***************************************************************
 * Name:      creeperApp.cpp
 * Purpose:   Code for Application Class
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

#include "creeperApp.h"
#include "creeperMain.h"

IMPLEMENT_APP(creeperApp);

bool creeperApp::OnInit()
{
    creeperFrame* frame = new creeperFrame(NULL, _("Comic Creeper"));
    //frame->SetIcon(wxICON(aaaa)); // To Set App Icon
    frame->Show();

    return true;
}

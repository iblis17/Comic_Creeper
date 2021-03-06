OBJDIR=./obj
BINDIR=./bin
TMPDIR=./tmp
LIBS=`curl-config --libs` `wx-config --libs` `pkg-config --libs libxml++-2.6`
CFLAGS=`wx-config --cppflags` `pkg-config --cflags libxml++-2.6`

all: creeperApp creeperMain
	g++ $(LIBS) $(CFLAGS) $(OBJDIR)/creeperMain.o $(OBJDIR)/creeperApp.o -o $(BINDIR)/creeper

creeperApp: creeperApp.cpp
	g++ $(LIBS) $(CFLAGS) -c creeperApp.cpp -o $(OBJDIR)/creeperApp.o

creeperMain: creeperMain.cpp
	g++ $(LIBS) $(CFLAGS) -c creeperMain.cpp -o $(OBJDIR)/creeperMain.o

init:
	mkdir -p $(OBJDIR) $(BINDIR) $(TMPDIR)

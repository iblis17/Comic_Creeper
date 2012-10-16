OBJDIR=./obj/
BINDIR=./bin/
LIBS=`curl-config --libs` `wx-config --libs`
CFLAGS=`wx-config --cppflags`

all: creeperApp creeperMain
	g++ $(LIBS) $(CFLAGS) $(OBJDIR)/creeperMain.o $(OBJDIR)/creeperApp.o -o $(BINDIR)/creeper

creeperApp: creeperApp.cpp
	g++ $(LIBS) $(CFLAGS) -c creeperApp.cpp -o $(OBJDIR)/creeperApp.o

creeperMain: creeperMain.cpp
	g++ $(LIBS) $(CFLAGS) -c creeperMain.cpp -o $(OBJDIR)/creeperMain.o

init:
	mkdir -p $(OBJDIR) $(BINDIR)

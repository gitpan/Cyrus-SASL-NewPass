#!/usr/bin/perl

# newpass.cgi -- A simple perl-script for changing saslpasswords after authenticating on the imap-server.
# "Copyright (c) Oliver Pitzeier, June 2001"
#                 o.pitzeier@uptime.at
#
# This script was written for one of our customers.
# The rest? not interessting I think :-)
#
# Changes are welcome, but please inform me about those changes!
#
# Many thanks to Marcel Grünauer and Bernd Pinter who helped me to do the first steps in perl.

# Things we use in this script.
use strict;
use warnings;

use CGI qw/:standard/;
use IMAP::Admin;

my $version        = 1.2;

# Those lines are defining some values for the CGI-frontend.
my $passlen        = 12;
my $userlen        = 30;
my $overridefields = 1;

# Define some values for connection to the local imap-server.
my $imap_port      = 143;
my $imap_seperator = ".";
my $imap           = undef;

# Print some basic html-stuff.
    print header;
    print start_html(-title  =>'Change your password',
                     -author =>'o.pitzeier@uptime.at',
                     -BGCOLOR=>'#C3CACE'),"\n";

# Create a table and a form.
    print "<table border=0>\n";
    print start_form,"\n",
        "<tr><td>username: </td><td>",            textfield(     -name        =>'login',
                                                                 -override    =>$overridefields,
                                                                 -size        =>$userlen,
                                                                 -maxlength   =>$userlen),"</td></tr>\n",
        "<tr><td>current password: </td><td>",    password_field(-name        =>'password',
                                                                 -override    =>$overridefields,
                                                                 -size        =>$passlen,
                                                                 -maxlength   =>$passlen),"</td></tr>\n",
        "<tr><td>new password: </td><td>",        password_field(-name        =>'newpass',
                                                                 -override    =>$overridefields,
                                                                 -size        =>$passlen,
                                                                 -maxlength   =>$passlen),"</td></tr>\n",
        "<tr><td>retype new password: </td><td>", password_field(-name        =>'retyped',
                                                                 -override    =>$overridefields,
                                                                 -size        =>$passlen,
                                                                 -maxlength   =>$passlen),"</td></tr>\n";
    print "</table>\n";
    print submit(-value=>'send'),"\n";
    print end_form,"\n";
    print hr;
# End of the table and the form.    

# Check the parameters and do some error-catching.
# The stuff down here should be self-explaining.
# The stuff with /tmp/.change is insecure and
# buggy. Think about two users changing their
# password. Someone should change this some day... :o)
# Maybe I will...
    if(param()) {
        if(param('login'))
        {
            if(param('newpass')) {
                if(param('retyped')) {
                    if(param('newpass') eq param('retyped')) {
                        $imap = IMAP::Admin->new('Server'    => 'localhost',
                                                 'Login'     => param('login'),
                                                 'Password'  => param('password'),
                                                 'Port'      => $imap_port,
                                                 'Separator' => $imap_seperator);
                        if($imap->error eq 'No Errors') {
                            my $command = "echo ".param('newpass'). " > /tmp/.change";
                            system($command);

                            $command = "./saslpasswd -p ".param('login')." < /tmp/.change";
                            if(system($command) == 0) {
                                print "Password has been changed!";
                            } else {
                                print "Something was wrong!";
                            }
                        } else {
                            if($imap->error =~ /Login failed/) {
                                if($imap->error =~ /: authentication/) {
                                    print "Wrong password! Could not log in.", br;
                                }
                                if($imap->error =~ /: user not found/) {
                                    print "User not found! Could not log in.", br;
                                }
                            }
                        $imap->close;
                        }
                    } else {
                        print "Retyped password doesnt match the new password!";
                    }
                } else {
                    print "New password was not retyped!";
                }
            } else {
                print "No new password given. Please enter your new password!";
            }
        } else {
            print "No username given. Please enter your username!";
        }
    } else {
        print "Please enter the above informations!";
    }
    print hr,"\n",end_html;

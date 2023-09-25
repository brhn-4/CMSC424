#!/usr/bin/env perl
#
# Reformats a relation file to more easily readable version.
#

my $nfile = $ARGV[1];
open $info, $ARGV[0] or die "Could not open $ARGV[0]";
my $l = <$info>;
$l =~ s/\s//g;
$l =~ s/\]\]/]]\n/g;
#print("$l\n");

if ($#ARGV > 0) {
    open(my $fh, '>', $nfile) or die "Could not open '$nfile'";
    print $fh "$l\n";
    close $fh;
    print "Wrote $nfile\n";
} else {
    print "$l\n";
}



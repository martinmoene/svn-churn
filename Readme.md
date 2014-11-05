svn-churn 
=========
A simple Python script to determine file churn and fix count of a Subversion repository [1].

Usage
-----

	Usage: svn-churn [options] [repos...]
	
	Options
	    -h, --help  this help screen
	            --  end options section
	    Other options upto -- are passed on to the 'svn log' command.
	
	svn-churn mines the log of the given Subversion repository
	and presents the number of changes and fixes for each file.
	Repos can be specified as a working copy path or a URL.
	
	Examples
	    Use repositories configured in script:
	        ./svn-churn.py
	
	    Use repositories configured in script and limit log used to latest 200 items:
	        ./svn-churn.py --limit 200 --
	
	    Report 50 most changed and fixed files (sort on changes*fixes):
	        ./svn-churn.py |sort -n -t , +2 | tail -n 50 |sort -r -n -t , +2
	
	Note
	    Among a few other things, you can configure the SVN repository in the script.

Example
-------
`svn-churn` creates output as shown below. 

Title line:

	Churn,Fixes,Churn*Fixes,File [repository...] 

The above title line disappears from the output in the following command:

	prompt>svn-churn.py --limit 200 -- https://svn.webkit.org/repository/webkit/trunk \
			|sort -n -t , +2 |grep -v ChangeLog |tail -n 10 |sort -r -n -t , +2
	14,3,42,/trunk/Source/WebKit2/UIProcess/mac/WKActionMenuController.mm
	8,4,32,/trunk/Source/WebCore/WebCore.exp.in
	5,5,25,/trunk/Source/WebKit2/WebProcess/WebPage/ios/WebPageIOS.mm
	7,3,21,/trunk/Source/WebKit2/WebKit2.xcodeproj/project.pbxproj
	5,4,20,/trunk/Source/WebCore/css/CSSSelector.cpp
	6,3,18,/trunk/Source/WebKit2/WebProcess/WebPage/WebPage.cpp
	4,4,16,/trunk/Source/WebCore/loader/cache/CachedRawResource.cpp
	5,3,15,/trunk/Source/WebKit2/CMakeLists.txt
	5,3,15,/trunk/Source/WebCore/WebCore.xcodeproj/project.pbxproj
	5,3,15,/trunk/Source/WebCore/CMakeLists.txt

Configuration
-------------
At the top of the script you can configure the following items.

### cfg_reposes 
`cfg_reposes` contains the default repositories to use.
 
	cfg_reposes = ['https://svn.webkit.org/repository/webkit/trunk']

### cfg_fixed_issues 
`cfg_fixed_issues` contains the patterns to recognise log message that concern a fix.

	cfg_fixed_issues = (
	    '[Ii]ssue[s]? #',
	    '[Ff]ix',
	    '[Cc]orrect'
	)

### cfg_edited_paths 
`cfg_edited_paths` allows you to specify patterns for partial paths with a replacement. This can be used to map paths used in the past to currently used paths, or to strip a path prefix. 

	cfg_edited_paths = (
	    ( r'/trunk/Source/core/', '/trunk/Source/WebCore/' ),
	    ( r'/trunk/Source/'     , ''                       ),
	 )

### cfg_svn 
`cfg_svn` specifies the (path of the) Subversion svn command to use.

	cfg_svn = 'svn'

References
----------
[1] Michael Feathers. [Getting Empirical about Refactoring](http://www.stickyminds.com/article/getting-empirical-about-refactoring). February 15, 2011.

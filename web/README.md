# Whip Website

This subdirectory contains the entire source for the [Whip Website](http://www.whip.services). 

## Running the Site

This is a [Middleman](http://middlemanapp.com) project, which builds a static site from these source files. We graciously forked this website from the [Hashicorp Middleman extension](https://github.com/hashicorp/middleman-hashicorp).


To run the site locally, just run the following commands:

```
$ bundle
$ bundle exec middleman build
$ bundle exec middleman run
```

Then open up `http://localhost:4567` in your browser. Middleman will try its best
to automatically reload the browser page as files change.

## Deploying

To deploy to GitHub pages, just do the following

```
$ rm -rf build
$ bundle exec middleman build
$ bundle exec middleman deploy
```

This will create a new branch `gh_pages` which you serve content directly from 
(i.e., through the GitHub project settings).


## Contributing

If you find a typo or you feel like you can improve the design or documentation, please
send us a pull request!

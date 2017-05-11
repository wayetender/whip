# Whip Website

This subdirectory contains the entire source for the [Whip Website](http://www.whip.services). 

## Running the Site

This is a [Middleman](http://middlemanapp.com) project, which builds a static site from these source files. We graciously forked this website from the [Hashicorp Middleman extension](https://github.com/hashicorp/middleman-hashicorp).


Just run the following commands:

```
$ bundle
$ bundle exec middleman build
$ bundle exec middleman run
```

Then open up `localhost:4567`.


## Contributing

If you find a typo or you feel like you can improve the design or documentation, please
send us a pull request!


## Deploying

To deploy, just do the following

```
$ rm -rf build
$ bundle exec middleman build
$ bundle exec middleman deploy


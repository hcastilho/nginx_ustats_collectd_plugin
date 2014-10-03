# nginx_ustats_collectd_plugin

[Collectd](http://collectd.org/) plugin to collect statistics from
[nginx](http://nginx.org/)
[ustats](https://github.com/nginx-modules/ngx_ustats_module) module.


## Installation
1. Add plugin configuration to collectd. Here is an example configuration:
```
TypesDB "/usr/share/collectd/types.db" "/usr/share/collectd/types.db"
<LoadPlugin python>
   Globals true
</LoadPlugin>
<Plugin python>
    ModulePath "/usr/lib/collectd/"
    LogTraces true
    Interactive false

    Import "nginx_ustats"
    <Module nginx_ustats>
        NginxUstatsURL "http://localhost/ustats?json=1"
    </Module>

</Plugin>
```

1. Place `nginx_ustats.py` where collectd python plugin is able to find it.
This is, any location in `sys.path` or locations added in `ModulePath`
directives in the collectd configuration. In the example config this is
`/usr/lib/collectd/`.

2. Place `nginx_ustats_types.db` in the location specified in the config.

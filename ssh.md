# 如何链接远程服务器

1.远程链接redis首先需要修改redis的配置文件redis.conf,这个文件在redis的目录下,我们使用vim编辑该文件.

2.进入到redis.conf后我们找到bind属性,该属性默认是127.0.0.1,意思是只能本机(服务器)访问,我们要远程链接需要把该属性注释掉,也可以改成物理机的ip也就只有自己能访问,我这里不写的意思就是所有人都可以访问

![img](https://img-blog.csdnimg.cn/8844fed72f9a4487a1a3bf430bb01d99.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)



3.继续往下找到requirepass属性,该属性是设置redis的密码,默认是没有密码一串空的字符串,需要我们自己设置密码(不设置密码也是可以的,但是有可能会被植入病毒所以为啦安全还是设置一下).

 ![img](https://img-blog.csdnimg.cn/4647b7db0d2f46e8a957283b642c6056.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)

 4.然后创建springboot项目测试一下,下面是所需要的依赖.



 ![img](https://img-blog.csdnimg.cn/90a7f239e14d4f66a3d9ddc2a521437e.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)

5.使用单元测试,导入RedisTemplate类.

![img](https://img-blog.csdnimg.cn/ceeb85a2fe284ef0829666a5b64ba9e7.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)

6.我们去服务器下查看我们刚set的键值对时发现都乱码啦,是因为RedisTemplate类的序列化默认使用的jdk序列化策略.解决办法有两种,第一种就是修改RedisTemplate类的序列化策略为StringRedisSerializer序列化策略,第二种办法使用StringRedisTrmaplate类.

![img](https://img-blog.csdnimg.cn/524d84d05fe44be48b4f8a20fa50dc34.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)

 7.我们使用StringRedisTemplate类来测试.

![img](https://img-blog.csdnimg.cn/3211f446f43c441e85b0d1d128dd0784.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)

再去服务器使用keys *查看所有key,这是就不会在乱码啦. 

 ![img](https://img-blog.csdnimg.cn/61a0fab11edd42fba83fcaa1497df39a.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5LiN6KaB5aSq6ZqP5L6_,size_20,color_FFFFFF,t_70,g_se,x_16)

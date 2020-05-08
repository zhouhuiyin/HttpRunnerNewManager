from django.shortcuts import render_to_response

def process(request, **kwargs):
    app = kwargs.pop('app', None)
    fun = kwargs.pop('function', None)
    index = kwargs.pop('id', None)

    if app == 'api':
        app = 'ApiManager'
    try:
        app = __import__("%s.views" % app)
        view = getattr(app, 'views')
        fun = getattr(view, fun)

        # 执行view.py中的函数，并获取其返回值
        result = fun(request, index) if index else fun(request)
    except (ImportError, AttributeError):
        #未找到对应的方法，返回404
        return render_to_response('404.html')

    return result

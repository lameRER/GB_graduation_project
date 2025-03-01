from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from shop.forms import ShopFaqForm
from shop.models import SoftwareCategory, Software, FeaturesSoftware, DevelopmentTeam, FAQ, Cart


def title_for_basic_template():
    text = 'Дипломный проект студентов GB'
    return text


def data_for_basic_template(request):
    cart_user = None

    if not request.user.is_anonymous:
        cart_user = Cart.objects.filter(user=request.user)

    data = {
        "software_category": SoftwareCategory.objects.all(),
        "cart": cart_user
    }
    return data


def all_soft():
    data = {
        "all_soft": Software.objects.all(),
        "software_operating_systems": Software.objects.filter(category__name='Операционные системы'),
        "software_office": Software.objects.filter(category__name='Офисное ПО'),
        "software_antivirus_protection": Software.objects.filter(category__name='Антивирусная защита')
    }
    return data


def index(request):
    title_index = 'Главная страница - '

    context = {
        "page_title": title_index + title_for_basic_template()
    }
    return render(request, 'index.html', {**context, **data_for_basic_template(request), **all_soft()})


def sitemap(request):
    title_sitemap = 'Карта сайта - '

    context = {
        'page_title': title_sitemap + title_for_basic_template()
    }
    return render(request, 'sitemap.html', {**context, **data_for_basic_template(request)})


def about_us(request):
    title_about_us = 'О нас / Наши контакты - '

    context = {
        "page_title": title_about_us + title_for_basic_template(),
        "development_team": DevelopmentTeam.objects.all(),
    }
    return render(request, 'about_us.html', {**context, **data_for_basic_template(request)})


def faq(request):
    title_faq = 'Полезная информация - '
    if request.method == 'POST':
        form = ShopFaqForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                UsersQuestions = form.save(commit=False)
                UsersQuestions.user = request.user
                UsersQuestions.save()
                return HttpResponseRedirect(reverse('faq'))
            except:
                form.add_error(None, 'Ошибка добавления')
    else:
        form = ShopFaqForm()
    context = {
        'page_title': title_faq + title_for_basic_template(),
        'faq': FAQ.objects.all(),
    }
    return render(request, 'faq.html', {**context, **data_for_basic_template(request), 'form': form})


def product(request):
    title_product = 'Описание программного обеспечения - '

    context = {
        'page_title': title_product + title_for_basic_template(),
    }
    return render(request, 'product.html', {**context, **data_for_basic_template(request)})


def products_catalog(request):
    title_product_catalog = 'Каталог программного обеспечения - '

    context = {
        "page_title": title_product_catalog + title_for_basic_template(),
    }
    return render(request, 'catalog.html', {**context, **data_for_basic_template(request), **all_soft()})


@login_required
def cart(request):
    title_cart = 'Корзина покупателя - '

    cart_user_small = Cart.objects.filter(user=request.user)

    cart_user_big = []

    for one_purchase in cart_user_small:
        featuresSoftware = FeaturesSoftware.objects.filter(id=one_purchase.software.id).first()

        new_line = {'image': one_purchase.software.image,
                    'name': one_purchase.software.name,
                    'software_id': one_purchase.software.id,
                    'one_purchase_id': one_purchase.id,
                    'description': featuresSoftware.description,
                    'operating_system': featuresSoftware.operating_system,
                    'video_card': featuresSoftware.video_card,
                    'hard_disk_mb': featuresSoftware.hard_disk_mb,
                    'min_ram_mb': featuresSoftware.min_ram_mb,
                    'quantity_in_card': one_purchase.quantity,
                    'software_price': one_purchase.software.price,
                    'one_purchase_sum': one_purchase.sum }

        cart_user_big.append(new_line)

    context = {
        'cart': cart_user_small,
        'big_cart': cart_user_big,
        'big_cart_total_sum': cart_user_small.total_sum,
        'page_title': title_cart + title_for_basic_template(),
    }
    return render(request, 'cart.html', context)


@login_required
def cart_add_one(request, software_id):
    user = request.user
    software = Software.objects.get(id=software_id)
    carts = Cart.objects.filter(user=user, software=software)

    if not carts.exists():
        Cart.objects.create(user=user, software=software, quantity=1)
    else:
        cart = carts.last()
        if software.quantity > cart.quantity:
            cart.quantity += 1
            cart.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def cart_delete_one(request, software_id):
    user = request.user
    software = Software.objects.get(id=software_id)
    carts = Cart.objects.filter(user=user, software=software)

    if carts.exists():
        cart = carts.last()

        if cart.quantity > 1:
            cart.quantity -= 1
            cart.save()
        # else:
        #    cart.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def cart_remove(request, cart_id):
    if Cart.objects.filter(id=cart_id).exists():
        Cart.objects.get(id=cart_id).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
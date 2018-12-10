# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, redirect
import datetime
import subprocess
import ConfigParser
from app01.utils import search_cert,auto_review

# Create your views here.

def command(cmd):
    ''' command is encoded with utf-8'''
    obj = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    stdout_res = obj.stdout.read()
    stderr_res = obj.stderr.read()
    return(stdout_res,stderr_res)

def search_main(request):
    if request.method == "GET":
        return render(request, "search.html")
    if request.method == "POST":
        device_name = request.POST.get("device_name")
        product_name = request.POST.get("product_name")
        model_name = request.POST.get("model_name")
        make_name = request.POST.get("make_name")
        cert_id = request.POST.get("cert_id")
        kbase = request.POST.get("kbase_keyword")
        account = request.POST.get("account_keyword")
        vendor = request.POST.get("vendor_keyword")
        TAM = request.POST.get("TAM_ack")
        TAM_vendor = request.POST.get("TAM_vendor")
        portal_case = request.POST.get("portal_case")

    if device_name:
        return redirect("/search/component/%s" %device_name)
    if product_name:
        return redirect("/search/product/%s" % product_name)
    if model_name:
        return redirect("/search/model/%s" % model_name)
    if make_name:
        return redirect("/search/make/%s" % make_name)
    if cert_id:
        return redirect("/search/leverage/%s" % cert_id)
    if kbase:
        return redirect("/search/kbase-title/%s" % kbase)
    if account:
        return redirect("/search/account-cert/%s" % account)
    if vendor:
        return redirect("/search/partner-cert/%s" % vendor)
    if TAM:
        return redirect("/search/TAM-ack-cert/%s" % TAM)
    if TAM_vendor:
        return redirect("/search/vendor-TAM/%s" % TAM_vendor)
    if portal_case:
        return redirect("/search/portal_id-case_number/%s" % portal_case)

    return HttpResponse("the search path is incorrect!")


def search_each(request,search_fun, search_param):
    # if 'closed' in search_cert.db.__str__():
    #     reload(search_cert)

    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        client_ip = request.META['REMOTE_ADDR']
    current_time = datetime.datetime.now()

    print("%s access at %s" % (client_ip, current_time))

    if search_fun == "component":
        result = search_cert.search_component(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "components.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'component_name': search_param})

    if search_fun == "product":
        result = search_cert.search_product(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "products.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'product': search_param})

    if search_fun == "model":
        result = search_cert.search_model(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "models.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'model_name': search_param})

    if search_fun == "make":
        result = search_cert.search_make(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "makes.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'make_name': search_param})


    if search_fun == "leverage":
        leverage_instance = auto_review.Leverage_Reivew(search_param)
        results = leverage_instance.generate_lev_result()
        result_list = results[0]
        if len(results[1]):
            ids_not_confirmed = results[1]
        else:
            ids_not_confirmed = None
        if len(results[2]):
            unconfirmed_cert_ids = results[2]
        else:
            unconfirmed_cert_ids = None
        print results
        return render(request, "leverages.html",
                  {'result_list': result_list, 'case_number': search_param, 'ids_not_confirmed':ids_not_confirmed, 'unconfirmed_cert_ids':unconfirmed_cert_ids})


    if search_fun == "kbase-title":
        result = search_cert.search_kbase(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "kbases.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'keyword_in_title': search_param})


    if search_fun == "account-cert":
        result = search_cert.search_cert_created_by_account(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "certs_created_by_account.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'account': search_param})

    if search_fun == "partner-cert":
        result = search_cert.search_cert_created_by_vendor(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "certs_created_by_vendor.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'vendor': search_param})


    if search_fun == "TAM-ack-cert":
        result = search_cert.search_TAM_ack_certs(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "TAM_ack_certs.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'TAM': search_param})

    if search_fun == "vendor-TAM":
        result = search_cert.search_TAM_by_vendor(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "vendor_TAM.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'vendor_tam': search_param})

    if search_fun == "portal_id-case_number":
        result = search_cert.search_case_number(search_param)
        result_list = result[0]
        number_intotal = result[1]
        return render(request, "portal_id-case_number.html",
                      {'result_list': result_list, 'number_intotal': number_intotal, 'portal_id': search_param})

    return HttpResponse("the search is invalid")

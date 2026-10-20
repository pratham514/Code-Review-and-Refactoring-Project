# sales_report.py - sales report script, as received for review.
# Reads an orders CSV and prints four reports.
# NOTE: kept unchanged on purpose. This is the "before" version.
import csv
import sys
import datetime

data = []
vips = ["alice", "bob"]
cancelled = 0
bad = 0
gross_total = 0
disc_total = 0
net_total = 0


def process(fn):
    global data, cancelled, bad, gross_total, disc_total, net_total
    f = open(fn)
    r = csv.reader(f)
    first = True
    for row in r:
        if first:
            first = False
            continue
        try:
            oid = row[0]
            c = row[1]
            p = row[2]
            cat = row[3]
            q = int(row[4])
            pr = float(row[5])
            d = row[6]
            s = row[7]
            datetime.datetime.strptime(d, "%Y-%m-%d")
            if s.strip().lower() == "cancelled":
                cancelled = cancelled + 1
            else:
                data.append([oid, c, p, cat, q, pr, d, s])
                g = q * pr
                rate = 0
                if q >= 50:
                    rate = 0.15
                else:
                    if q >= 10:
                        rate = 0.10
                    else:
                        rate = 0
                if c.lower() in vips:
                    rate = rate + 0.05
                if cat.lower() == "electronics":
                    rate = rate + 0.02
                if rate > 0.2:
                    rate = 0.2
                n = round(g * (1 - rate), 2)
                gross_total = gross_total + g
                disc_total = disc_total + (g - n)
                net_total = net_total + n
        except:
            bad = bad + 1
    f.close()


def summary():
    out = "== Summary ==\n"
    out = out + "Orders processed: " + str(len(data)) + "\n"
    out = out + "Cancelled skipped: " + str(cancelled) + "\n"
    out = out + "Invalid rows skipped: " + str(bad) + "\n"
    out = out + "Gross revenue: " + "%.2f" % gross_total + "\n"
    out = out + "Total discounts: " + "%.2f" % disc_total + "\n"
    out = out + "Net revenue: " + "%.2f" % net_total + "\n"
    return out


def cat_report():
    cats = []
    for row in data:
        q = row[4]
        pr = row[5]
        c = row[1]
        cat = row[3]
        g = q * pr
        rate = 0
        if q >= 50:
            rate = 0.15
        elif q >= 10:
            rate = 0.1
        if c.lower() in vips:
            rate = rate + 0.05
        if cat.lower() == "electronics":
            rate = rate + 0.02
        if rate > 0.2:
            rate = 0.2
        n = round(g * (1 - rate), 2)
        found = False
        for item in cats:
            if item[0] == cat.lower():
                item[1] = item[1] + n
                found = True
        if found == False:
            cats.append([cat.lower(), n])
    for i in range(len(cats)):
        for j in range(len(cats) - 1 - i):
            if cats[j][1] < cats[j + 1][1]:
                tmp = cats[j]
                cats[j] = cats[j + 1]
                cats[j + 1] = tmp
    out = "== Revenue by category ==\n"
    for item in cats:
        out = out + item[0].ljust(16) + "%10.2f" % item[1] + "\n"
    return out


def monthly_report():
    months = []
    for row in data:
        q = row[4]
        pr = row[5]
        c = row[1]
        cat = row[3]
        g = q * pr
        rate = 0
        if q >= 50:
            rate = 0.15
        elif q >= 10:
            rate = 0.1
        if c.lower() in vips:
            rate = rate + 0.05
        if cat.lower() == "electronics":
            rate = rate + 0.02
        if rate > 0.2:
            rate = 0.2
        n = round(g * (1 - rate), 2)
        key = row[6][:7]
        found = False
        for item in months:
            if item[0] == key:
                item[1] = item[1] + n
                found = True
        if found == False:
            months.append([key, n])
    i = 1
    while i < len(months):
        j = i
        while j > 0 and months[j - 1][0] > months[j][0]:
            tmp = months[j - 1]
            months[j - 1] = months[j]
            months[j] = tmp
            j = j - 1
        i = i + 1
    out = "== Monthly revenue ==\n"
    for item in months:
        out = out + item[0].ljust(16) + "%10.2f" % item[1] + "\n"
    return out


def top_report():
    custs = []
    for row in data:
        q = row[4]
        pr = row[5]
        c = row[1]
        cat = row[3]
        g = q * pr
        rate = 0
        if q >= 50:
            rate = 0.15
        elif q >= 10:
            rate = 0.1
        if cat.lower() == "electronics":
            rate = rate + 0.02
        if rate > 0.2:
            rate = 0.2
        n = round(g * (1 - rate), 2)
        found = False
        for item in custs:
            if item[0] == c.lower():
                item[1] = item[1] + n
                found = True
        if found == False:
            custs.append([c.lower(), n])
    for i in range(len(custs)):
        for j in range(len(custs) - 1 - i):
            if custs[j][1] < custs[j + 1][1]:
                tmp = custs[j]
                custs[j] = custs[j + 1]
                custs[j + 1] = tmp
    out = "== Top 3 customers ==\n"
    k = 0
    while k < 3 and k < len(custs):
        out = out + "%d. %-16s%10.2f" % (k + 1, custs[k][0], custs[k][1]) + "\n"
        k = k + 1
    return out


if __name__ == "__main__":
    fn = "orders.csv"
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    process(fn)
    print(summary() + "\n" + cat_report() + "\n" + top_report() + "\n" + monthly_report())

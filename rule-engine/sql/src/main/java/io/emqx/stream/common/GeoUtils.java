package io.emqx.stream.common;

import java.awt.geom.GeneralPath;
import java.awt.geom.Point2D;
import java.util.ArrayList;
import java.util.List;

public class GeoUtils {

    private static double rad(double d) {
        return d * Math.PI / 180.0;
    }

    /**
     * Get distance by lat and lng(unit:meters)
     */
    private static double getDistance(double lat1, double lng1, double lat2, double lng2) {
        double EARTH_RADIUS = 6378.137;
        double radLat1 = rad(lat1);
        double radLat2 = rad(lat2);
        double a = radLat1 - radLat2;
        double b = rad(lng1) - rad(lng2);
        double s = 2 * Math.asin(Math.sqrt(Math.pow(Math.sin(a / 2), 2) +
                Math.cos(radLat1) * Math.cos(radLat2) * Math.pow(Math.sin(b / 2), 2)));
        s = s * EARTH_RADIUS;
        s = Math.round(s * 10000d) / 10000d;
        return s;
    }


    public static boolean isInCircle(double lat1, double lng1, double lat2, double lng2, double radius) {
        double distance = getDistance(lat1, lng1, lat2, lng2);
        return !(distance > radius);
    }

    public static boolean isInPolygon(double pointLat, double pointLng, String pointArrayStr) {
        pointArrayStr = pointArrayStr.replace(" ", "");
        if (!pointArrayStr.startsWith("[[") || !pointArrayStr.endsWith("]]")) {
            throw new RuntimeException("Invalid parameter: " + pointArrayStr);
        }
        pointArrayStr = pointArrayStr.substring(2, pointArrayStr.length() - 2);
        String[] pointArray = pointArrayStr.split("],\\[");
        double[] latArray = new double[pointArray.length];
        double[] lngArray = new double[pointArray.length];
        int index = 0;
        for (String point : pointArray) {
            String[] points = point.split(",");
            if (points.length != 2) {
                throw new RuntimeException("Invalid parameters: " + pointArrayStr);
            }
            latArray[index] = Double.parseDouble(points[0]);
            lngArray[index] = Double.parseDouble(points[1]);
            index++;
        }
        return isInPolygon(pointLat, pointLng, latArray, lngArray);
    }


    @SuppressWarnings("WeakerAccess")
    public static boolean isInPolygon(double pointLat, double pointLng, double[] lat, double[] lng) {
        Point2D.Double point = new Point2D.Double(pointLng, pointLat);
        List<Point2D.Double> pointList = new ArrayList<>();
        double polygonPointX;
        double polygonPointY;
        for (int i = 0; i < lng.length; i++) {
            polygonPointX = lng[i];
            polygonPointY = lat[i];
            Point2D.Double polygonPoint = new Point2D.Double(polygonPointX, polygonPointY);
            pointList.add(polygonPoint);
        }
        return check(point, pointList);
    }


    private static boolean check(Point2D.Double point, List<Point2D.Double> polygon) {
        GeneralPath generalPath = new GeneralPath();

        Point2D.Double first = polygon.get(0);
        generalPath.moveTo(first.x, first.y);
        polygon.remove(0);
        for (Point2D.Double d : polygon) {
            generalPath.lineTo(d.x, d.y);
        }
        generalPath.lineTo(first.x, first.y);
        generalPath.closePath();
        return generalPath.contains(point);
    }

}

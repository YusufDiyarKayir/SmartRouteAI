namespace SmartRouteAI.Backend.Models;

// Google Directions API yanıt modeli
public class GoogleDirectionsResponse 
{
    public GoogleRoute[] routes { get; set; } = Array.Empty<GoogleRoute>();
}

public class GoogleRoute 
{
    public GoogleLeg[] legs { get; set; } = Array.Empty<GoogleLeg>();
    public GooglePolyline overview_polyline { get; set; } = new GooglePolyline();
}

public class GoogleLeg 
{
    public GoogleValue distance { get; set; } = new GoogleValue();
    public GoogleValue duration { get; set; } = new GoogleValue();
    public GoogleValue duration_in_traffic { get; set; } = new GoogleValue();
    public GoogleStep[] steps { get; set; } = Array.Empty<GoogleStep>();
}

public class GoogleStep 
{
    public string html_instructions { get; set; } = string.Empty;
}

public class GoogleValue 
{
    public double value { get; set; }
    public string text { get; set; } = string.Empty;
}

public class GooglePolyline 
{
    public string points { get; set; } = string.Empty;
}

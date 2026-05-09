using SQLite;

namespace FacturasOCR.Modelos;

// Tabla de SQLite para guardar cada factura procesada
[Table("InvoiceResult")] // nombre de la tabla en la BD (no tocar para no perder datos)
public class ResultadoFactura
{
    [PrimaryKey, AutoIncrement]
    public int Id { get; set; }

    public DateTime AnalyzedAt { get; set; }        // cuando se proceso
    public string ImagePath { get; set; } = "";      // ruta de la copia local
    public string RawText { get; set; } = "";         // texto completo del OCR
    public string FileName { get; set; } = "";        // nombre del archivo original

    // campos importantes que extrae Azure (o el fallback manual)
    public string VendorName { get; set; } = "";
    public string InvoiceId { get; set; } = "";
    public string InvoiceDate { get; set; } = "";
    public string Total { get; set; } = "";
}

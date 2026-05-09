using SQLite;
using FacturasOCR.Modelos;

namespace FacturasOCR.Servicios;

// Servicio para guardar/leer facturas en SQLite
public class ServicioBaseDatos
{
    // Carpeta por defecto donde se guarda la BD
    public static string DefaultDbDirectory =>
        Path.GetFullPath(Path.Combine(Environment.CurrentDirectory, "DatosFacturas"));

    private SQLiteAsyncConnection? _database;
    private string? _currentDbPath;

    // Devuelve la ruta del archivo .db
    public static string GetDbPath()
    {
        string dir = Preferences.Get("DbDirectory", DefaultDbDirectory);
        return Path.Combine(dir, "invoices.db");
    }

    // Conecta a la BD (la crea si no existe)
    private async Task<SQLiteAsyncConnection> GetConnectionAsync()
    {
        string dbPath = GetDbPath();

        // Si cambio la ruta, hay que reconectar
        if (_database != null && _currentDbPath == dbPath)
            return _database;

        _currentDbPath = dbPath;
        Directory.CreateDirectory(Path.GetDirectoryName(dbPath)!);
        _database = new SQLiteAsyncConnection(dbPath);
        await _database.CreateTableAsync<ResultadoFactura>();
        return _database;
    }

    // Guardar o actualizar una factura
    public async Task<int> SaveInvoiceAsync(ResultadoFactura invoice)
    {
        var db = await GetConnectionAsync();
        if (invoice.Id != 0)
            return await db.UpdateAsync(invoice);
        else
            return await db.InsertAsync(invoice);
    }

    // Sacar todas las facturas (las mas recientes primero)
    public async Task<List<ResultadoFactura>> GetAllInvoicesAsync()
    {
        var db = await GetConnectionAsync();
        return await db.Table<ResultadoFactura>()
                       .OrderByDescending(i => i.AnalyzedAt)
                       .ToListAsync();
    }

    public async Task<ResultadoFactura?> GetInvoiceAsync(int id)
    {
        var db = await GetConnectionAsync();
        return await db.Table<ResultadoFactura>()
                       .Where(i => i.Id == id)
                       .FirstOrDefaultAsync();
    }

    public async Task<int> DeleteInvoiceAsync(ResultadoFactura invoice)
    {
        var db = await GetConnectionAsync();
        return await db.DeleteAsync(invoice);
    }

    // Busca si ya hay una factura parecida (mismo nombre o contenido similar)
    public async Task<ResultadoFactura?> FindDuplicateAsync(string fileName, string rawText)
    {
        var db = await GetConnectionAsync();

        // Por nombre exacto
        var byName = await db.Table<ResultadoFactura>()
            .Where(i => i.FileName == fileName)
            .FirstOrDefaultAsync();
        if (byName != null)
            return byName;

        // Por contenido parecido
        if (!string.IsNullOrEmpty(rawText) && rawText.Length > 50)
        {
            string snippet = rawText.Substring(0, Math.Min(200, rawText.Length));
            var all = await db.Table<ResultadoFactura>().ToListAsync();
            var byContent = all.FirstOrDefault(i =>
                !string.IsNullOrEmpty(i.RawText) && i.RawText.Contains(snippet));
            if (byContent != null)
                return byContent;
        }

        return null;
    }
}

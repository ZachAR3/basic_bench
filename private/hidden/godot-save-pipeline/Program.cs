using Game.Persistence;
using System.Collections.Concurrent;
using System.Text.Json;

sealed class FakeFiles : IFileSystem
{
    public readonly ConcurrentDictionary<string, string> Data = new();
    public readonly List<(string Source, string Destination)> Moves = new();
    public bool CancelWrite;
    public async Task WriteAllTextAsync(string path, string contents, CancellationToken token)
    {
        Data[path] = contents;
        await Task.Yield();
        if (CancelWrite) throw new OperationCanceledException(token);
        token.ThrowIfCancellationRequested();
    }
    public Task<string> ReadAllTextAsync(string path, CancellationToken token) =>
        Task.FromResult(Data[path]);
    public void MoveReplace(string source, string destination)
    {
        Moves.Add((source, destination));
        Data[destination] = Data[source];
        Data.TryRemove(source, out _);
    }
    public bool Exists(string path) => Data.ContainsKey(path);
    public void Delete(string path) => Data.TryRemove(path, out _);
}

static class Program
{
    static void Require(bool value, string message)
    {
        if (!value) throw new Exception(message);
    }

    static async Task Atomic()
    {
        var files = new FakeFiles();
        var repository = new SaveRepository(files, "/saves");
        foreach (var invalid in new[] { "", "../x", "a/b", "é", "a\\b" })
        {
            try {
                await repository.SaveAsync(invalid, new(2, new()), default);
                throw new Exception("accepted invalid slot " + invalid);
            } catch (ArgumentException) { }
        }
        await repository.SaveAsync("slot-1", new(2, new() { ["score"] = 3L }), default);
        Require(files.Moves.Count == 1, "save was not atomically moved");
        Require(files.Moves[0].Source.EndsWith(".tmp"), "temporary name missing");
        Require(files.Moves[0].Destination == "/saves/slot-1.json", "wrong destination");

        files.CancelWrite = true;
        try {
            await repository.SaveAsync("cancel", new(2, new()), new CancellationToken(true));
            throw new Exception("cancellation ignored");
        } catch (OperationCanceledException) { }
        Require(!files.Data.Keys.Any(key => key.Contains("cancel.json.")), "temporary file leaked");
    }

    static async Task Migration()
    {
        var files = new FakeFiles();
        files.Data["/saves/old.json"] =
            """{"Version":1,"Data":{"coins":7,"unknown":{"items":[1,2]}}}""";
        var repository = new SaveRepository(files, "/saves");
        var first = await repository.LoadAsync("old", default);
        Require(first.Version == 2 && Convert.ToInt64(first.Data["currency"]) == 7, "migration failed");
        Require(!first.Data.ContainsKey("coins") && first.Data.ContainsKey("unknown"), "fields mishandled");
        ((Dictionary<string, object?>)first.Data["unknown"]!)["changed"] = true;
        var second = await repository.LoadAsync("old", default);
        Require(!((Dictionary<string, object?>)second.Data["unknown"]!).ContainsKey("changed"), "loads share state");
        files.Data["/saves/future.json"] = """{"Version":3,"Data":{}}""";
        try {
            await repository.LoadAsync("future", default);
            throw new Exception("future version accepted");
        } catch (InvalidDataException) { }
    }

    public static async Task Main(string[] args)
    {
        if (args[0] == "atomic") await Atomic();
        else if (args[0] == "migration") await Migration();
        else throw new ArgumentException(args[0]);
    }
}

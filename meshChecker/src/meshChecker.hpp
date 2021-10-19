#pragma once


// #include <maya/MApiNamespace.h>
#include <maya/MPxCommand.h>

#include <vector>
#include <string>
#include <mutex>


enum class MeshCheckType {
    TRIANGLES = 0,
    NGONS,
    NON_MANIFOLD_EDGES,
    LAMINA_FACES,
    BI_VALENT_FACES,
    ZERO_AREA_FACES,
    MESH_BORDER,
    CREASE_EDGE,
    ZERO_LENGTH_EDGES,
    UNFROZEN_VERTICES,
    EMPTY_GEOMETRY,
    TEST
};


class ResultStringArray {
    std::mutex mtx;
public:
    std::vector<std::string> data;
    void push_back(std::string x) {
        std::lock_guard<std::mutex> lock(mtx);
        data.push_back(x);
    }
};


class MeshChecker final : public MPxCommand {
public:
    static void* creator();
    static MSyntax newSyntax();

    // command interface
    MStatus doIt(const MArgList& argList) final;
    MStatus undoIt() final;
    MStatus redoIt() final;
    bool isUndoable() const final;

    //
    using Index = int;
    using IndexArray = std::vector<Index>;

    static IndexArray findTriangles(const MFnMesh&);
    static IndexArray findNgons(const MFnMesh&);
    static IndexArray findNonManifoldEdges(const MFnMesh&);
    static IndexArray findLaminaFaces(const MFnMesh&);
    static IndexArray findBiValentFaces(const MFnMesh&);
    static IndexArray findZeroAreaFaces(const MFnMesh&, double maxFaceArea);
    static IndexArray findMeshBorderEdges(const MFnMesh&);
    static IndexArray findCreaseEdges(const MFnMesh&);
    static IndexArray findZeroLengthEdges(const MFnMesh&, double minEdgeLength);
    static bool hasVertexPntsAttr(const MFnMesh&, bool fix);
    static bool isEmpty(const MFnMesh&);

    void checkMT(const MDagPath&, MeshCheckType ct);

private:
    MeshChecker();
    bool isMultiThreaded = false;
};
